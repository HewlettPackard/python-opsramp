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

    def test_get(self):
        group = self.client.resources()
        fake_result = ['unit', 'test', 'get']
        with requests_mock.Mocker() as m:
            url = group.api.compute_url()
            m.get(url, json=fake_result)
            actual = group.get()
            assert actual == fake_result

    def test_create(self):
        group = self.client.resources()
        fake_create_json = {
            'resourceName': 'ABBY-PC',
            'hostName': 'ABBY-PC',
            'aliasName': 'Server PC',
            'resourceType': 'server',
            'os': 'Ubuntu 14.04.6 LTS',
            'serialNumber': '1234-5678-901234'
        }
        fake_result = ['unit', 'test', 'create', 'result']
        with requests_mock.Mocker() as m:
            url = group.api.compute_url()
            m.post(url, json=fake_result)
            actual = group.create(definition=fake_create_json)
            assert actual == fake_result

    def test_update(self):
        group = self.client.resources()
        fake_resource_id = '123456'
        fake_update_json = {
            'os': 'Ubuntu 18.04.4 LTS'
        }
        fake_result = ['unit', 'test', 'update', 'result']
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(fake_resource_id)
            m.post(url, json=fake_result)
            actual = group.update(
                uuid=fake_resource_id,
                definition=fake_update_json
            )
            assert actual == fake_result

    def test_delete(self):
        group = self.client.resources()
        fake_resource_id = '789012'
        fake_result = ['unit', 'test', 'delete', 'result']
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(fake_resource_id)
            m.delete(url, json=fake_result)
            actual = group.delete(uuid=fake_resource_id)
            assert actual == fake_result

    def test_search(self):
        group = self.client.resources()
        fake_search_pattern = 'queryString=agentInstalled:true'
        fake_raw_result = ['unit', 'test', 'search', 'result']
        count = len(fake_raw_result)
        fake_cooked_result = {
            'totalResults': count,
            'pageSize': count,
            'totalPages': 1,
            'pageNo': 1,
            'previousPageNo': 0,
            'nextPage': False,
            'descendingOrder': False,
            'results': fake_raw_result
        }
        with requests_mock.Mocker() as m:
            url_suffix = 'search?{0}'.format(fake_search_pattern)
            url = group.api.compute_url(url_suffix)
            m.get(url, json=fake_raw_result)
            actual = group.search(pattern=fake_search_pattern)
            assert actual == fake_cooked_result

    def test_minimal(self):
        group = self.client.resources()
        fake_search_pattern = 'queryString=agentInstalled:true'
        fake_raw_result = ['unit', 'test', 'minimal', 'result']
        count = len(fake_raw_result)
        fake_cooked_result = {
            'totalResults': count,
            'pageSize': count,
            'totalPages': 1,
            'pageNo': 1,
            'previousPageNo': 0,
            'nextPage': False,
            'descendingOrder': False,
            'results': fake_raw_result
        }
        with requests_mock.Mocker() as m:
            url_suffix = 'minimal?{0}'.format(fake_search_pattern)
            url = group.api.compute_url(url_suffix)
            m.get(url, json=fake_raw_result)
            actual = group.minimal(pattern=fake_search_pattern)
            assert actual == fake_cooked_result

    def test_applications(self):
        group = self.client.resources()
        fake_resource_id = '789012'
        fake_raw_result = ['unit', 'test', 'applications', 'result']
        count = len(fake_raw_result)
        fake_cooked_result = {
            'totalResults': count,
            'pageSize': count,
            'totalPages': 1,
            'pageNo': 1,
            'previousPageNo': 0,
            'nextPage': False,
            'descendingOrder': False,
            'results': fake_raw_result
        }
        with requests_mock.Mocker() as m:
            url_suffix = '{0}/applications'.format(fake_resource_id)
            url = group.api.compute_url(url_suffix)
            m.get(url, json=fake_raw_result)
            actual = group.applications(uuid=fake_resource_id)
            assert actual == fake_cooked_result

    def test_availability(self):
        group = self.client.resources()
        # this a unix epoch timestamp. its actual value is not important, so
        # i just looked at the clock when i first wrote this function.
        fake_start = 1584727225
        fake_end = fake_start + (60 * 24)
        fake_resource_id = '789012'
        fake_result = ['unit', 'test', 'availability', 'result']
        with requests_mock.Mocker() as m:
            url_suffix = '{0}/availability?startTime={1}&endTime={2}'.format(
                fake_resource_id, fake_start, fake_end
            )
            url = group.api.compute_url(url_suffix)
            m.get(url, json=fake_result)
            actual = group.availability(
                uuid=fake_resource_id,
                start_epoch=fake_start,
                end_epoch=fake_end
            )
            assert actual == fake_result
