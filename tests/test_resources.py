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
import opsramp.resources


class StaticsTest(unittest.TestCase):
    def test_list2ormp_passthru(self):
        good1 = {'results': 'exist', 'totalResults': 12}
        result = opsramp.resources.list2ormp(good1)
        assert result is good1

    def test_list2ormp_conversion(self):
        list_form = [1, 2, 3, 4, 5, 6, 7, 8]
        count = len(list_form)
        canonical_form = {
            'totalResults': count,
            'pageSize': count,
            'totalPages': 1,
            'pageNo': 1,
            'previousPageNo': 0,
            'nextPage': False,
            'descendingOrder': False,
            'results': list_form
        }
        result = opsramp.resources.list2ormp(list_form)
        assert result == canonical_form

    def test_list2ormp_invalid(self):
        bad_ones = (
            3.14159,
            'string not allowed',
            {},
            {'big cow': 'close', 'small cow': 'far away'},
            {'results': 'not enough on their own'},
            {'totalResults': 0, 'noresults': 'bad'}
        )
        for bad1 in bad_ones:
            with self.assertRaises(AssertionError):
                opsramp.resources.list2ormp(bad1)


class ApiTest(unittest.TestCase):
    def setUp(self):
        fake_url = 'mock://api.example.com'
        fake_token = 'unit-test-fake-token'
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        self.fake_client_id = 'client_for_unit_test'
        self.client = self.ormp.tenant(self.fake_client_id)
        assert self.client.is_client()

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
        thisid = 333333
        fake_result = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url()
            m.post(url, json=fake_result, complete_qs=True)
            actual = group.create(definition=fake_create_json)
            assert actual == fake_result

    def test_update(self):
        group = self.client.resources()
        fake_resource_id = '123456'
        fake_update_json = {
            'os': 'Ubuntu 18.04.4 LTS'
        }
        fake_result = {'id': fake_resource_id}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(fake_resource_id)
            m.post(url, json=fake_result, complete_qs=True)
            actual = group.update(
                uuid=fake_resource_id,
                definition=fake_update_json
            )
            assert actual == fake_result

    def test_delete(self):
        group = self.client.resources()
        fake_resource_id = '789012'
        fake_result = {'id': fake_resource_id}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(fake_resource_id)
            m.delete(url, json=fake_result, complete_qs=True)
            actual = group.delete(uuid=fake_resource_id)
            assert actual == fake_result

    def test_search(self):
        # The OpsRamp "resources" API returns flat lists of results
        # instead of the usual multi-value result struct, for no
        # apparent reason. Our Python classes are supposed to handle
        # that and return a normal result struct so that the caller
        # doesn't need to know. Check that it's doing this.
        group = self.client.resources()
        fake_search_pattern = 'queryString=agentInstalled:true'
        fake_raw_result = ['unit', 'test', 'search', 'values']
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
            m.get(url, json=fake_raw_result, complete_qs=True)
            actual = group.search(pattern=fake_search_pattern)
            assert actual == fake_cooked_result

    def test_minimal(self):
        # The OpsRamp "resources" API returns flat lists of results
        # instead of the usual multi-value result struct, for no
        # apparent reason. Our Python classes are supposed to handle
        # that and return a normal result struct so that the caller
        # doesn't need to know. Check that it's doing this.
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
            m.get(url, json=fake_raw_result, complete_qs=True)
            actual = group.minimal(pattern=fake_search_pattern)
            assert actual == fake_cooked_result

    def test_applications(self):
        # The OpsRamp "resources" API returns flat lists of results
        # instead of the usual multi-value result struct, for no
        # apparent reason. Our Python classes are supposed to handle
        # that and return a normal result struct so that the caller
        # doesn't need to know. Check that it's doing this.
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
            m.get(url, json=fake_raw_result, complete_qs=True)
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
            m.get(url, json=fake_result, complete_qs=True)
            actual = group.availability(
                uuid=fake_resource_id,
                start_epoch=fake_start,
                end_epoch=fake_end
            )
            assert actual == fake_result

    def test_get_templates(self):
        group = self.client.resources()
        fake_resource_id = '789012'
        fake_result = ['unit', 'test', 'availability', 'result']
        with requests_mock.Mocker() as m:
            url_suffix = '{0}/templates/search?{1}'.format(
                fake_resource_id, "fake_pattern"
            )
            url = group.api.compute_url(url_suffix)
            m.get(url, json=fake_result, complete_qs=True)
            actual = group.get_templates(
                uuid=fake_resource_id,
                pattern="fake_pattern"
            )
            assert actual['results'] == fake_result
