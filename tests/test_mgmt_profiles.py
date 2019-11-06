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


class ApiTest(unittest.TestCase):
    def setUp(self):
        fake_url = 'http://api.example.com'
        fake_token = 'unit-test-fake-token'
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        self.fake_client_id = 'client_for_unit_test'
        self.client = self.ormp.tenant(self.fake_client_id)
        assert self.client.is_client()

        self.group = self.client.mgmt_profiles()
        assert 'Profiles' in str(self.group)

    def test_search(self):
        pattern = 'whatever'
        url = self.group.api.compute_url('search?%s' % pattern)
        expected = ['unit', 'test', 'list']
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected)
            actual = self.group.search(pattern)
        assert actual == expected

    def test_create(self):
        url = self.group.api.compute_url()
        expected = {'id': 345678}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = self.group.create(definition=expected)
        assert actual == expected

    def test_update(self):
        thisid = 123456
        url = self.group.api.compute_url(thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = self.group.update(uuid=thisid, definition=expected)
        assert actual == expected

    def test_delete(self):
        thisid = 789012
        url = self.group.api.compute_url(thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.delete(url, json=expected)
            actual = self.group.delete(uuid=thisid)
        assert actual == expected

    def test_attach(self):
        thisid = 345678
        url = self.group.api.compute_url('%s/attach' % thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = self.group.attach(uuid=thisid)
        assert actual == expected

    def test_detach(self):
        thisid = 901234
        url = self.group.api.compute_url('%s/detach' % thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = self.group.detach(uuid=thisid)
        assert actual == expected

    def test_reconnect(self):
        thisid = 901234
        url = self.group.api.compute_url('%s/reconnectTunnel' % thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected)
            actual = self.group.reconnect(uuid=thisid)
        assert actual == expected
