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

        self.first_response = self.client.first_response()
        assert 'First_Response' in str(self.first_response)

        self.model_training = self.client.model_training()
        assert 'ModelTraining' in str(self.model_training)

    def test_search(self):
        group = self.first_response
        for pattern, expected in (
            ('', ['unit', 'test', 'results']),
            ('pageNo=1&pageSize=100&is&sortName=id', ['more', 'nonsense'])
        ):
            if pattern:
                url = group.api.compute_url('?' + pattern)
            else:
                url = group.api.compute_url()
            with requests_mock.Mocker() as m:
                m.get(url, json=expected, complete_qs=True)
                actual = group.search(pattern)
            assert actual == expected

    def test_policy_detail(self):
        group = self.first_response
        thisid = 789012
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(thisid)
            m.get(url, json=expected, complete_qs=True)
            actual = group.policy_detail(uuid=thisid)
            assert actual == expected

    def test_create(self):
        group = self.first_response
        expected = {'id': 345678}
        fake_defn = {'name': 'dougal'}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url()
            m.post(url, json=expected, complete_qs=True)
            actual = group.create(definition=fake_defn)
            assert actual == expected

    def test_update(self):
        group = self.first_response
        thisid = 123456
        expected = {'id': thisid}
        fake_defn = {'name': 'ted'}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(thisid)
            m.post(url, json=expected, complete_qs=True)
            actual = group.update(uuid=thisid, definition=fake_defn)
            assert actual == expected

    def test_delete(self):
        group = self.first_response
        thisid = 789012
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url(thisid)
            m.delete(url, json=expected, complete_qs=True)
            actual = group.delete(uuid=thisid)
            assert actual == expected

    def test_enable(self):
        group = self.first_response
        thisid = 345678
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('%s/enable' % thisid)
            m.post(url, json=expected, complete_qs=True)
            actual = group.enable(uuid=thisid)
            assert actual == expected

    def test_disable(self):
        group = self.first_response
        thisid = 901234
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('%s/disable' % thisid)
            m.post(url, json=expected, complete_qs=True)
            actual = group.disable(uuid=thisid)
            assert actual == expected

    def test_model_training(self):
        group = self.model_training
        expected = "sample text"
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('train/ALERT_FIRST_RESPONSE_TRAINING')
            m.post(url, text=expected, complete_qs=True)
            actual = group.train_model()
            assert actual == expected

    def test_file_upload(self):
        group = self.model_training
        expected = "sample text"
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('files')
            with open('tests/testing.csv', 'rb') as x:
                file = {'attachment': ('testing.csv', x, 'text/csv')}
                data = {'test': 'fake'}
                m.post(url, text=expected, complete_qs=True)
                actual = group.file_upload(data, file)
                assert actual == expected

    def test_get_training_file(self):
        group = self.model_training
        expected = {
            "results": [
                {
                    "name": "sample"
                }
            ],
            "totalResults": 1,
            "orderBy": "createdTime",
            "pageNo": 1,
            "pageSize": 100,
            "totalPages": 1,
            "nextPage": False,
            "previousPageNo": 0,
            "descendingOrder": True
        }
        with requests_mock.Mocker() as m:
            url = group.api.compute_url('files')
            m.get(url, json=expected, complete_qs=True)
            actual = group.get_training_file()
            assert actual == expected
