#!/usr/bin/env python
#
# (c) Copyright 2020-2022 Hewlett Packard Enterprise Development LP
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

        self.service_maps = self.client.service_maps()
        assert 'serviceGroups' in str(self.service_maps)

    def test_service_maps_get_root(self):
        group = self.service_maps
        thisid = 111111
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('search')
            m.get(url, json=expected, complete_qs=True)
            actual = group.get()
            assert actual == expected

    def test_service_maps_get_child(self):
        group = self.service_maps
        thisid = 222222
        expected = {'id': thisid}
        sgid = 'some-sgid'
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('%s/childs/search' % sgid)
            m.get(url, json=expected, complete_qs=True)
            # test uuid parameter specifically.
            actual = group.get(uuid=sgid)
            assert actual == expected
            # test that uuid is the first parameter
            actual = group.get(sgid)
            assert actual == expected

    def test_service_maps_get_minimal(self):
        group = self.service_maps
        thisid = 333333
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('minimal')
            m.get(url, json=expected, complete_qs=True)
            actual = group.get(minimal=True)
            assert actual == expected

    def test_service_maps_create(self):
        group = self.service_maps
        thisid = 444444
        expected = {'id': thisid}
        fake_defn = {'name': 'fr dick byrne'}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url()
            m.post(url, json=expected, complete_qs=True)
            actual = group.create(definition=fake_defn)
            assert actual == expected

    def test_service_maps_update(self):
        group = self.service_maps
        thisid = 123456
        expected = {'id': thisid}
        fake_defn = {'name': 'fr todd unctious'}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(thisid)
            m.post(url, json=expected, complete_qs=True)
            actual = group.update(uuid=thisid, definition=fake_defn)
            assert actual == expected

    def test_service_maps_delete(self):
        group = self.service_maps
        thisid = 789012
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(thisid)
            m.delete(url, json=expected, complete_qs=True)
            actual = group.delete(uuid=thisid)
            assert actual == expected
