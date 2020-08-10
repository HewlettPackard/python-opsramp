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

        self.first_response = self.client.first_response()
        assert 'First_Response' in str(self.first_response)

    def test_search(self):
        group = self.first_response
        url = group.api.compute_url()
        expected = ['unit', 'test', 'list']
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected)
            actual = group.search()
        assert actual == expected

    def test_policy_detail(self):
        group = self.first_response
        thisid = 789012
        url = group.api.compute_url(thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected)
            actual = group.policy_detail(uuid=thisid)
        assert actual == expected

    def test_create(self):
        group = self.first_response
        url = group.api.compute_url()
        expected = {'id': 345678}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.create(definition=expected)
        assert actual == expected

    def test_update(self):
        group = self.first_response
        thisid = 123456
        url = group.api.compute_url(thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.update(uuid=thisid, definition=expected)
        assert actual == expected

    def test_delete(self):
        group = self.first_response
        thisid = 789012
        url = group.api.compute_url(thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.delete(url, json=expected)
            actual = group.delete(uuid=thisid)
        assert actual == expected

    def test_enable(self):
        group = self.first_response
        thisid = 345678
        url = group.api.compute_url('%s/enable' % thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.enable(uuid=thisid)
        assert actual == expected

    def test_disable(self):
        group = self.first_response
        thisid = 901234
        url = group.api.compute_url('%s/disable' % thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.disable(uuid=thisid)
        assert actual == expected
