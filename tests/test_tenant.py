#!/usr/bin/env python
#
# (c) Copyright 2019-2022 Hewlett Packard Enterprise Development LP
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

import opsramp.binding
import requests_mock


class TenantTest(unittest.TestCase):
    def setUp(self):
        fake_url = "mock://api.example.com"
        fake_token = "unit-test-fake-token"
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        fake_client_id = "client_for_unit_test"
        self.client = self.ormp.tenant(fake_client_id)
        assert self.client.is_client()

        fake_msp_id = "msp_for_unit_test"
        self.msp = self.ormp.tenant(fake_msp_id)
        assert not self.msp.is_client()

    def test_agent_script(self):
        with requests_mock.Mocker() as m:
            url = self.client.api.compute_url("agents/deployAgentsScript")
            expected = "unit test fake agent content"
            m.get(url, text=expected, complete_qs=True)
            actual = self.client.get_agent_script()
            assert actual == expected
            assert m.call_count == 1

    def test_clients(self):
        # A partner object can have clients contained within it.
        assert not self.msp.is_client()
        assert self.msp.clients()
        # A client object cannot have other clients nested inside it
        # so it should raise an assertion if we try to access them.
        assert self.client.is_client()
        with self.assertRaises(AssertionError):
            assert self.client.clients()

    def test_methods_exist(self):
        assert self.client.rba()
        assert self.client.monitoring()
        assert self.client.policies()
        assert self.client.discovery()
        assert self.client.integrations()
        assert self.client.credential_sets()
        assert self.client.roles()
