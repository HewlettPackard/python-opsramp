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


class ApiTest(unittest.TestCase):
    def setUp(self):
        fake_url = 'mock://api.example.com'
        fake_token = 'unit-test-fake-token'
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        self.fake_client_id = 'client_for_unit_test'
        self.client = self.ormp.tenant(self.fake_client_id)
        assert self.client.is_client()

        self.escalations = self.client.escalations()
        assert 'Escalations' in str(self.escalations)

    def test_search(self):
        group = self.escalations
        thisid = 123456
        expected = {'id': thisid}
        pattern = 'queryString=name:Test+allList:true'
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('search?%s' % pattern)
            m.get(url, json=expected, complete_qs=True)
            actual = group.search(pattern)
            assert actual == expected

    def test_create(self):
        group = self.escalations
        thisid = 345678
        expected = {'id': thisid}
        fake_definition = {'name': 'elvis'}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url()
            m.post(url, json=expected, complete_qs=True)
            actual = group.create(definition=fake_definition)
            assert actual == expected

    def test_update(self):
        group = self.escalations
        thisid = 123456
        expected = {'id': thisid}
        fake_definition = {'name': 'elvis'}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(thisid)
            m.post(url, json=expected, complete_qs=True)
            actual = group.update(uuid=thisid, definition=fake_definition)
            assert actual == expected

    def test_delete(self):
        group = self.escalations
        thisid = 789012
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(thisid)
            m.delete(url, json=expected, complete_qs=True)
            actual = group.delete(uuid=thisid)
            assert actual == expected

    def test_enable(self):
        group = self.escalations
        thisid = 345678
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('%s/enable' % thisid)
            m.post(url, json=expected, complete_qs=True)
            actual = group.enable(uuid=thisid)
            assert actual == expected

    def test_disable(self):
        group = self.escalations
        thisid = 901234
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('%s/disable' % thisid)
            m.post(url, json=expected)
            actual = group.disable(uuid=thisid)
            assert actual == expected
