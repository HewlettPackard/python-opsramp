#!/usr/bin/env python
#
# (c) Copyright 2019-2020 Hewlett Packard Enterprise Development LP
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
import requests_mock

import opsramp.binding


class BindingTest(unittest.TestCase):
    def setUp(self):
        endpoint = 'mock://api.example.com'
        key = 'opensesame'
        secret = 'thereisnospoon'
        token = 'fake-unit-test-token'

        url = endpoint + '/auth/oauth/token'
        hshake = 'grant_type=client_credentials&client_id=%s&client_secret=%s'
        expected_send = hshake % (key, secret)
        expected_receive = {'access_token': token}
        expected_auth = {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json,application/xml'
        }
        with requests_mock.Mocker() as m:
            adapter = m.post(url, json=expected_receive, complete_qs=True)
            self.ormp = opsramp.binding.connect(
                endpoint,
                key,
                secret
            )
            assert m.call_count == 1
            assert adapter.last_request.text == expected_send
            assert type(self.ormp) is opsramp.binding.Opsramp
            assert self.ormp.auth == expected_auth

    def test_str(self):
        assert 'Opsramp' in str(self.ormp)

    def test_config(self):
        obj = self.ormp.config()
        assert 'GlobalConfig' in str(obj)

    def test_tenant(self):
        obj = self.ormp.tenant('unit-test')
        assert 'Tenant' in str(obj)
