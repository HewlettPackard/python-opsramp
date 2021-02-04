#!/usr/bin/env python
#
# (c) Copyright 2019-2021 Hewlett Packard Enterprise Development LP
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

import unittest
from requests import codes as http_status
from mock import MagicMock
import requests_mock

# Note we are deliberately using simplejson (instead of json) because
# that's what the requests module uses and we want to raise the same
# types of exceptions, not exceptions from the generic "json" module.
import simplejson

import opsramp.base


class FakeResp(object):
    def __init__(self, content, request):
        self.status_code = http_status.OK
        self.content = content
        self.text = simplejson.dumps(self.content)
        self.json_fail = False
        self.request = request

    def json(self):
        content = self.content
        if self.json_fail:
            # deliberately cause a parsing exception
            content = 'deliberately bad JSON for unit test purposes!!'
        return content


class ApiObjectTest(unittest.TestCase):
    def setUp(self):
        self.fake_url = 'mock://api.example.com'
        self.fake_token = 'ffffffffffffffff'
        self.fake_auth = {
            'Authorization': 'Bearer %s' % self.fake_token,
            'Accept': 'application/json'
        }
        self.ao = opsramp.base.ApiObject(
            self.fake_url,
            self.fake_auth.copy()
        )
        assert 'ApiObject' in str(self.ao)

    def test_shared_session(self):
        '''All clones should share the requests session'''
        ao2 = self.ao.clone()
        assert ao2.session is self.ao.session

    def test_compute_url(self):
        # some value, doesn't really matter.
        suffix = 'unit/test/value'
        expected = self.ao.baseurl + '/' + suffix
        assert self.ao.compute_url(suffix) == expected
        # empty string and None should both return the root path.
        rootdir = self.ao.baseurl
        assert self.ao.compute_url() == rootdir
        assert self.ao.compute_url('/') == rootdir
        assert self.ao.compute_url('') == rootdir
        assert self.ao.compute_url(None) == rootdir

    # We're not testing an exhaustive set of suffix patterns here because
    # that is already being done by the PathTracker unit tests.
    def test_cd(self):
        # some value, doesn't really matter.
        suffix = 'unit/test/cd'
        expected = self.ao.compute_url() + '/' + suffix
        actual = self.ao.cd(suffix)
        assert actual == expected
        assert self.ao.compute_url() == expected
        # check the root path works.
        rootdir = self.ao.baseurl
        self.ao.cd('/random/place1')
        assert self.ao.compute_url() != rootdir
        assert self.ao.cd('/') == rootdir
        assert self.ao.compute_url() == rootdir
        # no args should default to the root path.
        self.ao.cd('/random/place0')
        assert self.ao.compute_url() != rootdir
        assert self.ao.cd() == rootdir
        assert self.ao.compute_url() == rootdir
        # empty string should default to the root path.
        self.ao.cd('/random/place2')
        assert self.ao.compute_url() != rootdir
        assert self.ao.cd('') == rootdir
        assert self.ao.compute_url() == rootdir
        # None should default to the root path.
        self.ao.cd('/random/place3')
        assert self.ao.cd(None) == rootdir
        assert self.ao.compute_url() == rootdir

    # We're not testing an exhaustive set of suffix patterns here because
    # that is already being done by the PathTracker unit tests.
    def test_pushpopd(self):
        suffix = 'unit/test/pushd'
        base = self.ao.compute_url()
        expected = base + '/' + suffix
        actual = self.ao.pushd(suffix)
        assert actual == expected
        assert self.ao.compute_url() == expected
        actual = self.ao.popd()
        assert actual == base
        assert self.ao.compute_url() == base

    def test_headers(self):
        expected = self.fake_auth.copy()
        actual = self.ao.prep_headers({})
        assert actual == expected

        expected = self.fake_auth.copy()
        custom = {
            'color': 'pink',
            'distance': 'far'
        }
        expected.update(custom)
        actual = self.ao.prep_headers(custom)
        assert actual == expected

        # The caller is supposed to be able to override any of the standard
        # auth headers by providing its own value. Check this works.
        expected = self.fake_auth.copy()
        key = 'Authorization'
        assert key in expected
        testvalue = 'open sesame'
        assert expected[key] != testvalue
        custom[key] = testvalue
        actual = self.ao.prep_headers(custom)
        assert actual[key] == testvalue
        expected.update(custom)
        assert actual == expected

    def test_results(self):
        # Test successful response

        with requests_mock.mock() as m:
            expected = {'hello': 'world'}
            m.get(self.fake_url, json=expected, status_code=http_status.OK)

            faked_response = FakeResp(
                content=expected,
                request=self.ao.session.get(self.fake_url).request
            )
            actual = self.ao.process_result(self.fake_url, faked_response)
            assert type(actual) is dict
            assert actual == expected

        # Test response where result is not valid JSON
        with requests_mock.mock() as m:
            expected = 'deliberately bad JSON for unit test purposes!!'
            m.get(self.fake_url, text=expected)

            faked_response = FakeResp(
                content=['nothing'],
                request=self.ao.session.get(self.fake_url).request
            )

            faked_response.json_fail = True

            actual = self.ao.process_result(self.fake_url, faked_response)
            assert type(actual) is str
            assert actual == expected

        # Test that exception is thrown if unexpected HTTP status code returned
        with requests_mock.mock() as m:
            m.get(
                self.fake_url,
                status_code=http_status.BAD_REQUEST,
                text='Pretending to fail horribly'
            )

            faked_response = FakeResp(
                content=['nothing'],
                request=self.ao.session.get(self.fake_url).request
            )
            faked_response.status_code = http_status.BAD_REQUEST

            failed = False
            try:
                actual = self.ao.process_result(self.fake_url, faked_response)
            except RuntimeError as e:
                print(e)
                failed = True
            assert failed

    def test_paginated_results(self):
        # Define three pages of test data that return the following result
        # data:
        # Page 1: 1-10
        # Page 2: 11-20
        # Page 3: 21-30
        # If the pagination works, the result should be the range 1-30.
        request_responses = []
        for result_page in range(3):
            result_data = list(
                range((10 * result_page) + 1, (10 * result_page) + 11)
            )

            response_body = {
                'results': result_data,
                'totalResults': 30,
                'pageNo': result_page + 1,
                'pageSize': 10,
                'nextPage': (result_page < 2),
                'previousPageNo': result_page,
                'descendingOrder': False
            }

            response = {
                'status_code': http_status.OK,
                'json': response_body,
            }

            request_responses.append(response)

        # Build up the list of expected result data based on what we're feeding
        # in to the mock.
        expected = []
        for response in request_responses:
            expected = expected + response['json']['results']

        with requests_mock.mock() as m:
            # Feed the mock with the three responses it should return
            m.get(self.fake_url, request_responses)

            # Build the initial (faked) response based on the above
            faked_response = FakeResp(
                content=request_responses[0]['json'],
                request=self.ao.session.get(self.fake_url).request
            )
            actual = self.ao.process_result(self.fake_url, faked_response)
            assert type(actual) is dict

            # So that no existing code is broken, the behaviour emulates the
            # existing behaviour of the API except that it acts as if the data
            # was in one big page.
            assert actual['results'] == expected
            assert actual['totalResults'] == len(expected)
            assert actual['nextPage'] is False
            assert actual['pageNo'] == 1
            assert actual['previousPageNo'] == 0

        # Test that if the request is not a HTTP GET, complain:
        fake_get_request = MagicMock()
        fake_get_request.method = 'FAKE'
        expected = ['request is not GET']
        actual = self.ao.collate_pages(fake_get_request, expected)
        assert actual == expected

        # Test that it handles the lack of a "results" fields in the data
        # correctly
        fake_get_request.method = 'GET'
        expected = ['request does not contain results key']
        actual = self.ao.collate_pages(fake_get_request, expected)
        assert actual == expected

        # Test that if the next page is not retrieved successfully, an empty
        # result is returned.
        with requests_mock.mock() as m:
            m.get(
                self.fake_url,
                status_code=http_status.BAD_REQUEST,
                json=['should not be seen']
            )

            fake_get_request = MagicMock()
            fake_get_request.method = 'GET'
            fake_get_request.url = self.fake_url

            page_1_data = {
                'results': ['should not be seen'],
                'nextPage': True,
                'pageNo': 1
            }

            actual = self.ao.collate_pages(fake_get_request, page_1_data)
            assert actual['results'] == []
            assert actual['totalResults'] == 0
            assert actual['pageSize'] == 0

    def test_get(self):
        with requests_mock.Mocker() as m:
            url = self.ao.compute_url()
            expected = 'unit test get result'
            m.get(url, text=expected)
            actual = self.ao.get()
            assert actual == expected

    def test_put(self):
        with requests_mock.Mocker() as m:
            url = self.ao.compute_url()
            expected = 'unit test put result'
            m.put(url, text=expected)
            actual = self.ao.put()
            assert actual == expected

    def test_post(self):
        with requests_mock.Mocker() as m:
            url = self.ao.compute_url()
            expected = 'unit test post result'
            m.post(url, text=expected)
            actual = self.ao.post()
            assert actual == expected

    def test_delete(self):
        with requests_mock.Mocker() as m:
            url = self.ao.compute_url()
            expected = 'unit test delete result'
            m.delete(url, text=expected)
            actual = self.ao.delete()
            assert actual == expected

    def test_patch(self):
        with requests_mock.Mocker() as m:
            url = self.ao.compute_url()
            expected = 'unit test patch result'
            m.patch(url, text=expected)
            actual = self.ao.patch()
            assert actual == expected
