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
        fake_url = "mock://api.example.com"
        fake_token = "unit-test-fake-token"
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        self.fake_client_id = "client_for_unit_test"
        self.client = self.ormp.tenant(self.fake_client_id)
        assert self.client.is_client()

    def test_get(self):
        group = self.client.resource_groups()
        fake_raw_result = ["unit", "test", "get", "result"]
        with requests_mock.Mocker() as m:
            url_suffix = "/search"
            url = group.api.compute_url(url_suffix)
            m.get(url, json=fake_raw_result)
            actual = group.get()
            assert actual == fake_raw_result

    def test_create(self):
        group = self.client.resource_groups()
        fake_create_json = {
            "resourceName": "ABBY-PC",
            "hostName": "ABBY-PC",
            "aliasName": "Server PC",
            "resourceType": "server",
            "os": "Ubuntu 14.04.6 LTS",
            "serialNumber": "1234-5678-901234",
        }
        thisid = 333333
        fake_result = {"id": thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url()
            m.post(url, json=fake_result, complete_qs=True)
            actual = group.create(definition=fake_create_json)
            assert actual == fake_result

    def test_update(self):
        group = self.client.resource_groups()
        fake_resource_id = "123456"
        fake_update_json = {"os": "Ubuntu 18.04.4 LTS"}
        fake_result = {"id": fake_resource_id}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(fake_resource_id)
            m.post(url, json=fake_result, complete_qs=True)
            actual = group.update(uuid=fake_resource_id, definition=fake_update_json)
            assert actual == fake_result

    def test_delete(self):
        group = self.client.resource_groups()
        fake_resource_id = "789012"
        fake_result = {"id": fake_resource_id}
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
        group = self.client.resource_groups()
        fake_search_pattern = "queryString=agentInstalled:true"
        fake_raw_result = ["unit", "test", "search", "values"]
        count = len(fake_raw_result)
        fake_cooked_result = {
            "totalResults": count,
            "pageSize": count,
            "totalPages": 1,
            "pageNo": 1,
            "previousPageNo": 0,
            "nextPage": False,
            "descendingOrder": False,
            "results": fake_raw_result,
        }
        with requests_mock.Mocker() as m:
            url_suffix = "search?{0}".format(fake_search_pattern)
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
        group = self.client.resource_groups()
        fake_search_pattern = "queryString=agentInstalled:true"
        fake_raw_result = ["unit", "test", "minimal", "result"]
        count = len(fake_raw_result)
        fake_cooked_result = {
            "totalResults": count,
            "pageSize": count,
            "totalPages": 1,
            "pageNo": 1,
            "previousPageNo": 0,
            "nextPage": False,
            "descendingOrder": False,
            "results": fake_raw_result,
        }
        with requests_mock.Mocker() as m:
            url_suffix = "minimal?{0}".format(fake_search_pattern)
            url = group.api.compute_url(url_suffix)
            m.get(url, json=fake_raw_result, complete_qs=True)
            actual = group.minimal(pattern=fake_search_pattern)
            assert actual == fake_cooked_result
