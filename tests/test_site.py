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

        self.sites = self.client.sites()
        assert 'Sites' in str(self.sites)

    def test_site_search(self):
        group = self.sites
        pattern = 'whatever'
        url = group.api.compute_url('search?%s' % pattern)
        expected = ['unit', 'test', 'list']
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected)
            actual = group.search(pattern)
        assert actual == expected

    def test_site_create(self):
        group = self.sites
        url = group.api.compute_url()
        expected = {'id': 345678}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.create(definition=expected)
        assert actual == expected

    def test_site_update(self):
        group = self.sites
        thisid = 123456
        url = group.api.compute_url(thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.update(uuid=thisid, definition=expected)
        assert actual == expected

    def test_site_delete(self):
        group = self.sites
        thisid = 789012
        url = group.api.compute_url(thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.delete(url, json=expected)
            actual = group.delete(uuid=thisid)
        assert actual == expected

    def test_site_get_id(self):
        group = self.sites
        thisid = 345678
        url = group.api.compute_url(thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            m.get(url, json=expected)
            actual = group.get(thisid)
            assert actual == expected

    def test_site_get_list(self):
        group = self.sites
        url = group.api.compute_url('minimal')
        expected = ['unit', 'test', 'list']
        with requests_mock.Mocker() as m:
            m.get(url, json=expected)
            # default suffix should be "minimal"
            actual = group.get()
            assert actual == expected
            # specific suffix
            actual = group.get('minimal')
            assert actual == expected
