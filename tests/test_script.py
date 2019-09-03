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
import base64
import requests_mock

from opsramp.base import Helpers
from opsramp.rba import Category
import opsramp.binding


class StaticsTest(unittest.TestCase):
    def test_encode_payload(self):
        testfile = 'README.md'
        with open(testfile, 'rb') as f:
            expected = f.read()
        actual64 = Helpers.b64encode_payload(testfile)
        actual = base64.b64decode(actual64)
        assert actual == expected

    def test_mkAttachment(self):
        tvalues = {
            'name': 'whatever.sh',
            'content': 'random stuff'
        }
        actual = Category.mkAttachment(
            name=tvalues['name'],
            payload=tvalues['content']
        )
        expected = {
            'name': tvalues['name'],
            'file': tvalues['content']
        }
        assert actual == expected

    def test_mkBadParameter(self):
        with self.assertRaises(AssertionError):
            Category.mkParameter(
                name='pname', description='pdesc', datatype='STRING',
                optional=True
                # deliberately missing default value
            )

    def test_mkGoodParameter(self):
        tvalues = {
            'name': 'venue',
            'description': 'Where am I today?',
            'type': 'STRING'
        }
        actual = Category.mkParameter(
            name=tvalues['name'],
            description=tvalues['description'],
            datatype=tvalues['type']
        )
        actual = Category.mkParameter(
            name=tvalues['name'],
            description=tvalues['description'],
            datatype=tvalues['type']
        )
        expected = {
            'name': tvalues['name'],
            'description': tvalues['description'],
            'dataType': tvalues['type'],
            'type': 'REQUIRED',
            'defaultValue': None
        }
        assert actual == expected

    def test_mkBadScript(self):
        with self.assertRaises(AssertionError):
            Category.mkScript(
                name='sname', description='pdesc', platforms=['LINUX'],
                execution_type='Firing squad is not valid',
                payload_file='README.md'
            )
        with self.assertRaises(AssertionError):
            Category.mkScript(
                name='sname', description='pdesc', platforms=['LINUX'],
                execution_type='COMMAND',
                payload='if there is a payload',
                payload_file='cannot have payload_file as well'
            )

    def test_mkGoodScript(self):
        p1 = Category.mkParameter(
            name='venue',
            description='Where am I today?',
            datatype='STRING'
        )
        tvalues = {
            'name': 'Hello <venue>',
            'description': 'Stereotypical rock star intro',
            'platforms': ['LINUX'],
            'type': 'COMMAND',
            'payload': 'echo "hello $1"',
            'parameters': [p1]
        }
        actual = Category.mkScript(
            name=tvalues['name'],
            description=tvalues['description'],
            platforms=tvalues['platforms'],
            execution_type=tvalues['type'],
            payload=tvalues['payload'],
            parameters=tvalues['parameters']
        )
        expected = {
            'name': tvalues['name'],
            'description': tvalues['description'],
            'platforms': tvalues['platforms'],
            'executionType': tvalues['type'],
            'command': tvalues['payload'],
            'parameters': tvalues['parameters']
        }
        assert actual == expected


class ApiTest(unittest.TestCase):
    def setUp(self):
        fake_url = 'https://api.example.com'
        fake_token = 'unit-test-fake-token'
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        self.fake_client_id = 'client_for_unit_test'
        self.client = self.ormp.tenant(self.fake_client_id)
        assert self.client.is_client()

        self.rba = self.client.rba()
        assert 'Rba' in str(self.rba)

    def test_categories(self):
        group = self.rba.categories()
        assert group
        expected = ['unit', 'test', 'list']
        assert expected
        with requests_mock.Mocker() as m:
            url = group.api.compute_url()
            m.post(url, json=expected)
            actual = group.create(
                name='unit-test-category-A'
            )
            assert actual == expected
            actual = group.create(
                name='unit-test-category-B',
                parent_uuid=123456
            )
            assert actual == expected

    def test_one_category(self):
        this1 = self.rba.categories().category('unit-test-1')
        assert this1
        expected = {'unit': 'test'}
        assert expected
        with requests_mock.Mocker() as m:
            url = this1.api.compute_url()
            m.post(url, json=expected)
            actual = this1.create(
                definition=expected
            )
            assert actual == expected
