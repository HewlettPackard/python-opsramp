#!/usr/bin/env python
#
# (c) Copyright 2020-2023 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from contextlib import contextmanager
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import StringIO
import logging
import socket
import sys
from threading import Thread
import unittest

from opsramp.base import ApiObject, ApiWrapper
import requests

# Define a list of "canned" responses here. These are used to test the retry
# capability of the API client, so that when faced with a response containing a
# HTTP 429 (Too Many Requests) status code, it should keep retrying until some
# maximum limit is reached.
CANNED_RESPONSES = [
    {"code": 429, "message": b"Failed attempt #1"},
    {"code": 429, "message": b"Failed attempt #2"},
    {"code": 429, "message": b"Failed attempt #3"},
    {"code": 200, "message": b"Succeeded on fourth attempt"},
]


# Borrowed from https://gist.github.com/mogproject/fc7c4e94ba505e95fa03
@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class MockServerRequestHandler(BaseHTTPRequestHandler, object):
    def __init__(self, request, client_address, server):
        # Creating this reference to the server as that is where the current
        # server instance's copies of the canned responses live; a new request
        # handler is generated for each request so they can't live here.
        self.http_server = server
        super(MockServerRequestHandler, self).__init__(request, client_address, server)

    def do_GET(self):
        logging.debug("running do_GET()")

        if len(self.http_server.canned_responses) > 0:
            # We have at least one more "canned" response to send...
            response = self.http_server.canned_responses.pop(0)
            logging.debug("Sending response: %s" % response)

            # Send the header including the status code
            self.send_response(code=response["code"])
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            # Write the message body to self.wfile
            self.wfile.write(response["message"])

            # self.canned_responses = self.canned_responses[1:]
            logging.debug(
                "%d responses remain" % len(self.http_server.canned_responses)
            )
        else:
            # If we run out of canned responses just send back a HTTP 500
            # (Internal Server Error). The idea is that the retry logic should
            # give up before the test server runs out of canned responses and
            # that this is here just for completeness.
            self.send_response(code=500)

            self.send_header("Content-type", "text/plain")
            self.end_headers()

            self.wfile.write(b"Internal Server Error")

        return


class MockHttpServer(HTTPServer, object):
    def __init__(self, server_address, RequestHandlerClass, canned_responses):
        # Need to subclass HTTPServer so that I can define a set of canned
        # responses that will be consumed by MockServerRequestHandler.
        logging.warning("Standing up HTTP Server")
        self.canned_responses = canned_responses
        super(MockHttpServer, self).__init__(server_address, RequestHandlerClass)


class MockWebClient:
    """Minimal web client to generate requests against our mock web server"""

    def __init__(self, host="localhost", port=80):
        self.host = host
        self.port = port

    def get(self):
        return requests.get("http://%s:%d/test" % (self.host, self.port))


class TestMockServer(unittest.TestCase):
    def setUp(self):
        self.server_port = self.get_free_port()
        logging.info("Creating HTTP server on port %d" % self.server_port)
        self.mock_server = MockHttpServer(
            ("localhost", self.server_port),
            MockServerRequestHandler,
            deepcopy(CANNED_RESPONSES),
        )

        # Create the server in a separate thread so that it can run in parallel
        # with the client (i.e. tests) being run against it.
        self.mock_server_thread = Thread(target=self.mock_server.serve_forever)
        if hasattr(self.mock_server_thread, "daemon"):
            self.mock_server_thread.daemon = True
        else:
            self.mock_server_thread.setDaemon(True)
        self.mock_server_thread.start()

    def tearDown(self):
        logging.info("Shutting down Mock HTTP server")
        self.mock_server.shutdown()
        return super(TestMockServer, self).tearDown()

    @classmethod
    def get_free_port(cls):
        """Get the system to open a TCP socket (and let it choose the port
        number). Once it's been created successfully, shut down the empty
        server attached to that socket and return the port number to be
        "recycled" for use with the test server.

        Returns:
            int -- Available TCP Port number
        """
        s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        s.bind(("localhost", 0))
        _, port = s.getsockname()
        s.close()
        return port

    def test__mock_server_works(self):
        # Test that the web server returns all canned responses, in order.
        client = MockWebClient(host="localhost", port=self.server_port)

        for expected in CANNED_RESPONSES:
            response = client.get()

            self.assertEqual(response.status_code, expected["code"])
            self.assertEqual(response.content, expected["message"])

    def test__apiwrapper_retry_logic(self):
        fake_url = "http://localhost:%d/" % self.server_port
        fake_token = "ffffffffffffffff"
        fake_auth = {
            "Authorization": "Bearer %s" % fake_token,
            "Accept": "application/json",
        }

        api_object = ApiObject(fake_url, fake_auth.copy())
        assert "ApiObject" in str(api_object)

        api_stub = "whatevs"
        api_wrapper = ApiWrapper(api_object, api_stub)

        api_endpoint = "foo"
        with captured_output() as (out, err):
            api_wrapper.api.get("/%s" % api_endpoint)

        expected_requests = []
        for resp in CANNED_RESPONSES:
            req = '"GET /%s/%s HTTP/1.1" %d' % (api_stub, api_endpoint, resp["code"])
            expected_requests.append(req)

        lines = err.getvalue().splitlines()

        # Check each GET request to verify that it gets the correct status code
        # (basically, 429 three times then a 200) to confirm that the retry
        # logic is doing its thing
        for index in range(len(lines)):
            self.assertIn(expected_requests[index], lines[index])
