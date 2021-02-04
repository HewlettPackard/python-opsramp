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
import requests_mock

import opsramp.binding


class MonitoringTest(unittest.TestCase):
    def setUp(self):
        fake_url = 'mock://api.example.com'
        fake_token = 'unit-test-fake-token'
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        self.fake_client_id = 'client_for_unit_test'
        self.client = self.ormp.tenant(self.fake_client_id)
        assert self.client.is_client()

        self.monitoring = self.client.monitoring()
        assert 'Monitoring' in str(self.monitoring)

    def test_templates(self):
        group = self.monitoring.templates()
        thisid = 888888
        expected = {'id': thisid}
        pattern = 'whatever'
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('search?%s' % pattern)
            m.get(url, json=expected, complete_qs=True)
            actual = group.search(pattern)
            assert actual == expected
