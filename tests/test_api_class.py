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
