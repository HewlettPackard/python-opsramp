#!/usr/bin/env python
#
# (c) Copyright 2020 Hewlett Packard Enterprise Development LP
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


class ResourcesText(unittest.TestCase):
    def setUp(self):
        fake_url = 'https://api.example.com'
        fake_token = 'unit-test-fake-token'
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        self.fake_client_id = 'client_for_unit_test'
        self.client = self.ormp.tenant(self.fake_client_id)
        assert self.client.is_client()

    def test_resources(self):
        group = self.client.resources()
        assert group
        expected = ['unit', 'test', 'list']
        assert expected
        with requests_mock.Mocker() as m:
            url = group.api.compute_url()
            m.get(url, json=expected)
            actual = group.get()
            assert actual == expected

            url = group.api.compute_url()
            m.post(url, json=expected)
            actual = group.create(definition=expected)
            assert actual == expected
