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
    def setUp(self):
        self.testfile = 'tox.ini'
        with open(self.testfile, 'rb') as f:
            self.content_raw = f.read()
        self.content_64 = Helpers.b64encode_payload(self.testfile)
        # assert that base64 encoding is working.
        raw = base64.b64decode(self.content_64)
        assert raw == self.content_raw

    def test_mkAttachment(self):
        tvalues = {
            'name': self.testfile,
            'content': self.content_raw
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
        expected = {
            'name': tvalues['name'],
            'description': tvalues['description'],
            'dataType': tvalues['type'],
            'type': 'REQUIRED',
            'defaultValue': None
        }
        assert actual == expected

    def test_mkBadScript(self):
        tvalues = {
            'name': 'sname',
            'description': 'pdesc',
            'platforms': ['LINUX']
        }
        with self.assertRaises(AssertionError):
            Category.mkScript(
                execution_type='Firing squad is not valid',
                name=tvalues['name'],
                description=tvalues['description'],
                platforms=tvalues['platforms'],
                payload_file=self.testfile
            )
        with self.assertRaises(AssertionError):
            Category.mkScript(
                execution_type='COMMAND',
                name=tvalues['name'],
                description=tvalues['description'],
                platforms=tvalues['platforms'],
                payload='if there is a payload',
                payload_file='cannot have payload_file as well'
            )

    def test_mkGoodCommandScript(self):
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

    def test_mkGoodPythonScript(self):
        tvalues = {
            'name': 'Hello <venue>',
            'description': 'Python rock star intro',
            'platforms': ['LINUX'],
            'type': 'PYTHON',
            'process_name': 'jabberwocky',
            'service_name': 'silmarilion',
            'install_timeout': 'a really long time'
        }
        actual = Category.mkScript(
            name=tvalues['name'],
            description=tvalues['description'],
            platforms=tvalues['platforms'],
            execution_type=tvalues['type'],
            script_name=self.testfile,
            payload_file=self.testfile,
            install_timeout=tvalues['install_timeout'],
            process_name=tvalues['process_name'],
            service_name=tvalues['service_name']
        )
        expected = {
            'name': tvalues['name'],
            'description': tvalues['description'],
            'platforms': tvalues['platforms'],
            'executionType': tvalues['type'],
            'attachment': {
                'name': self.testfile,
                'file': self.content_64
            },
            'installTimeout': tvalues['install_timeout'],
            'processName': tvalues['process_name'],
            'serviceName': tvalues['service_name']
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

        parent = {'id': 123456, 'name': 'unit-test-parent-category'}
        child = {'id': 789012, 'name': 'unit-test-child-category'}

        with requests_mock.Mocker() as m:
            # we will be doing two posts so mock both results now.
            url = group.api.compute_url()
            m.post(url, [{'json': parent}, {'json': child}])

            # Create a category with no parent ID specified
            actual = group.create(
                name=parent['name']
            )
            assert actual == parent

            # Create a category with parent ID specified
            actual = group.create(
                name=child['name'],
                parent_uuid=parent['id']
            )
            assert actual == child

    def test_delete_category(self):
        category_group = self.rba.categories()
        assert category_group
        categoryID = 12345
        expected = ''
        with requests_mock.Mocker() as m:
            url = category_group.api.compute_url(categoryID)
            m.delete(url, text=expected)
            actual = category_group.delete(uuid=categoryID)
            assert actual == expected

    def test_update_category(self):
        category_group = self.rba.categories()
        assert category_group
        categoryID = 12345
        updated_name = 'some new name'
        expected = {
            'id': categoryID,
            'name': updated_name
        }

        with requests_mock.Mocker() as m:
            url = category_group.api.compute_url()
            m.put(url, json=expected)
            actual = category_group.update(categoryID, {
                'name': updated_name
            })
            assert actual == expected

    def test_create_script(self):
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

    def test_update_script(self):
        this1 = self.rba.categories().category('unit-test-1')
        assert this1
        scriptId = 12345
        expected = {'unit': 'test'}
        assert expected
        with requests_mock.Mocker() as m:
            url = this1.api.compute_url(scriptId)
            m.post(url, json=expected)
            actual = this1.update(
                uuid=scriptId, definition=expected
            )
            assert actual == expected

    def test_delete_script(self):
        this1 = self.rba.categories().category('unit-test-1')
        assert this1
        scriptId = 67890
        expected = ''
        with requests_mock.Mocker() as m:
            url = this1.api.compute_url(scriptId)
            m.delete(url, text=expected)
            actual = this1.delete(uuid=scriptId)
            assert actual == expected
