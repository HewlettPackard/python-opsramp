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
import requests_mock

import opsramp.binding


class BindingTest(unittest.TestCase):
    def setUp(self):
        fake_url = 'http://api.example.com'
        fake_key = 'opensesame'
        fake_secret = 'thereisnospoon'
        fake_token = 'fake-unit-test-token'
        with requests_mock.Mocker() as m:
            url = fake_url + '/auth/oauth/token'
            expected = '{"access_token": "%s"}' % fake_token
            m.post(url, text=expected)
            self.ormp = opsramp.binding.connect(
                fake_url,
                fake_key,
                fake_secret
            )
        assert type(self.ormp) is opsramp.binding.Opsramp
        assert 'Opsramp' in str(self.ormp)

    def test_config(self):
        obj = self.ormp.config()
        assert 'GlobalConfig' in str(obj)

    def test_tenant(self):
        obj = self.ormp.tenant('unit-test')
        assert 'Tenant' in str(obj)
