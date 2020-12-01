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


class GlobalConfigTest(unittest.TestCase):
    def setUp(self):
        fake_url = 'mock://api.example.com'
        fake_token = 'unit-test-fake-token'
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)
        self.gconfig = self.ormp.config()
        assert 'GlobalConfig' in str(self.gconfig)

    def test_simple_urls(self):
        fnmap = {
            '/alertTypes': self.gconfig.get_alert_types,
            '/cfg/countries': self.gconfig.get_countries,
            '/cfg/timezones': self.gconfig.get_timezones,
            '/cfg/alertTechnologies': self.gconfig.get_alert_technologies,
            '/cfg/tenants/channels': self.gconfig.get_channels,
            '/cfg/devices/types': self.gconfig.get_device_types
        }
        for suffix, fn in fnmap.items():
            with requests_mock.Mocker() as m:
                url = self.ormp.api.compute_url(suffix)
                # all these methods return lists so create a nonsense one.
                expected = ['unit', 'test']
                expected.extend(suffix.split('/'))
                assert expected
                m.get(url, json=expected, complete_qs=True)
                actual = fn()
                assert actual == expected

    # Test the bizarre special cases around NOT FOUND that are
    # documented in the definitiom of get_nocs.
    def test_irregular_urls(self):
        fnmap = {
            '/cfg/tenants/nocs': self.gconfig.get_nocs
        }
        for suffix, fn in fnmap.items():
            with requests_mock.Mocker() as m:
                # rig the mock to raise an exception on "get"
                url = self.ormp.api.compute_url(suffix)
                expected = 'nonsense unit test value'
                for eclass in (RuntimeError, AssertionError, Exception):
                    m.get(url, exc=eclass('omg the sky is falling'))
                    with self.assertRaises(eclass):
                        actual = fn()
                # now try the special case exception that fn() *should* handle.
                expected = []
                m.get(url, exc=RuntimeError('"code":"0005" rien de rien'))
                actual = fn()
                assert actual == expected
