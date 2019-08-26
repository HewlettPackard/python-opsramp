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
import requests_mock

import opsramp.binding


class GlobalConfigTest(unittest.TestCase):
    def setUp(self):
        fake_url = 'http://api.example.com'
        fake_token = 'unit-test-fake-token'
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)
        self.gconfig = self.ormp.config()
        assert 'GlobalConfig' in str(self.gconfig)

    def test_urls(self):
        for fn, suffix in (
            (self.gconfig.get_alert_types, '/alertTypes'),
            (self.gconfig.get_countries, '/cfg/countries'),
            (self.gconfig.get_timezones, '/cfg/timezones'),
            (self.gconfig.get_alert_technologies, '/cfg/alertTechnologies'),
            (self.gconfig.get_channels, '/cfg/tenants/channels'),
            (self.gconfig.get_nocs, '/cfg/tenants/nocs'),
            (self.gconfig.get_device_types, '/cfg/devices/types')
        ):
            with requests_mock.Mocker() as m:
                url = self.ormp.api.compute_url(suffix)
                # all these methods return lists so create a nonsense one.
                expected = ['unit', 'test'].extend(suffix.split('/'))
                m.get(url, text=json.dumps(expected))
                actual = fn()
                assert actual == expected
