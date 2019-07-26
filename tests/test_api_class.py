#!/usr/bin/env python
#
# (c) Copyright 2019 Hewlett Packard Enterprise Development LP
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

from __future__ import print_function
import unittest
import json
from requests import codes as http_status
import requests_mock

import opsramp.binding


class FakeResp(object):
    def __init__(self, content):
        self.status_code = http_status.OK
        self.content = content
        self.text = str(self.content)
        self.json_fail = False

    def json(self):
        if self.json_fail:
            raise RuntimeError('deliberate json_fail')
        return json.loads(self.content)


class ApiOjectTest(unittest.TestCase):
    def setUp(self):
        self.fake_url = 'http://api.example.com'
        self.fake_token = 'ffffffffffffffff'
        self.fake_auth = {
            'Authorization': 'Bearer %s' % self.fake_token,
            'Accept': 'application/json'
        }
        self.ao = opsramp.binding.ApiObject(
            self.fake_url,
            self.fake_auth.copy()
        )
        assert 'ApiObject' in str(self.ao)
        self.awrapper = opsramp.binding.ApiWrapper(self.ao, 'whatevs')
        assert 'ApiWrapper' in str(self.awrapper)

    def test_compute_url(self):
        suffix = 'unit/test/value'
        expected = self.ao.compute_url() + '/' + suffix
        assert self.ao.compute_url(suffix) == expected

    # We're not testing an exhaustive set of suffix patterns here because
    # that is already being done by the PathTracker unit tests.
    def test_cd(self):
        suffix = 'unit/test/cd'
        expected = self.ao.compute_url() + '/' + suffix
        actual = self.ao.cd(suffix)
        assert actual == expected
        assert self.ao.compute_url() == expected

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
        expected = {'hello': 'world'}
        fake_resp = FakeResp(json.dumps(expected))
        actual = self.ao.process_result(self.fake_url, fake_resp)
        assert type(actual) is dict
        assert actual == expected

        fake_resp.json_fail = True
        actual = self.ao.process_result(self.fake_url, fake_resp)
        assert type(actual) is str
        assert json.loads(actual) == expected

        fake_resp.status_code = http_status.BAD_REQUEST
        with self.assertRaises(RuntimeError):
            self.ao.process_result(self.fake_url, fake_resp)

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

    # We're not testing an exhaustive set of suffix patterns here because
    # that is already being done by the ApiObject unit tests.
    def test_wrapped_get(self):
        with requests_mock.Mocker() as m:
            url = self.awrapper.api.compute_url()
            expected = 'unit test wrapped get result'
            m.get(url, text=expected)
            actual = self.awrapper.get()
            assert actual == expected
