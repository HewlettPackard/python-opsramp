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
import datetime
import requests_mock

from opsramp.msp import Clients
import opsramp.binding


class StaticsTest(unittest.TestCase):
    def setUp(self):
        self.hours = {
            'businessStartHour': 10,
            'businessStartMin': 40,
            'businessEndHour': 19,
            'businessEndMin': 23,
            'businessDayStart': 1,
            'businessDayEnd': 4,
            'smsVoiceNotification': True
        }
        self.client = {
            'name': 'unit test client',
            'address': 'Springfield',
            'timeZone': 'America/Los_Angeles',
            'country': 'United States',
        }

    def test_mkHours(self):
        actual = Clients.mkHours(
            day_start=datetime.time(
                self.hours['businessStartHour'],
                self.hours['businessStartMin']
            ),
            day_end=datetime.time(
                self.hours['businessEndHour'],
                self.hours['businessEndMin']
            ),
            week_start=self.hours['businessDayStart'],
            week_end=self.hours['businessDayEnd'],
            sms_voice_notification=self.hours['smsVoiceNotification']
        )
        assert actual == self.hours

    def test_mkClient(self):
        # use the default "hours" value first.
        actual = Clients.mkClient(
            name=self.client['name'],
            address=self.client['address'],
            time_zone=self.client['timeZone'],
            country=self.client['country']
        )
        assert actual == self.client
        # now a specific hours definition
        self.client['clientDetails'] = self.hours
        actual = Clients.mkClient(
            name=self.client['name'],
            address=self.client['address'],
            time_zone=self.client['timeZone'],
            country=self.client['country'],
            hours=self.hours
        )
        assert actual == self.client
        # remove the hours specifier again, for the next test.
        del self.client['clientDetails']


class ApiTest(unittest.TestCase):
    def setUp(self):
        fake_url = 'https://api.example.com'
        fake_token = 'unit-test-fake-token'
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        self.fake_msp_id = 'msp_for_unit_test'
        self.msp = self.ormp.tenant(self.fake_msp_id)
        assert not self.msp.is_client()

    def test_api(self):
        group = self.msp.clients()
        assert group
        expected = ['unit', 'test', 'list']
        assert expected
        url = group.api.compute_url('search')
        with requests_mock.Mocker() as m:
            m.get(url, json=expected)
            # one search variant
            actual = group.search('whatever')
            assert actual == expected
            # the other search variant
            actual = group.search_for_prefix('pre-whatever')
            assert actual == expected

        url = group.api.compute_url('minimal')
        with requests_mock.Mocker() as m:
            m.get(url, json=expected)
            # default suffix
            actual = group.get()
            assert actual == expected
            # specific suffix
            actual = group.get('minimal')
            assert actual == expected

        url = group.api.compute_url()
        with requests_mock.Mocker() as m:
            m.post(url, json=expected)
            assert 'name' not in expected
            # the name field is missing so we should get an error.
            with self.assertRaises(AssertionError):
                actual = group.create(definition=expected)
        # now let's try a valid one.
        fake_definition = {
            'name': 'elvis',
            'address': 'graceland',
            'timeZone': 'UTC',
            'country': 'US'
        }
        with requests_mock.Mocker() as m:
            m.post(url, json=fake_definition)
            actual = group.create(definition=fake_definition)
            assert actual == fake_definition

        thisid = 123456
        url = group.api.compute_url(thisid)
        with requests_mock.Mocker() as m:
            m.post(url, json=fake_definition)
            actual = group.update(
                uuid=thisid,
                definition=fake_definition
            )
            assert actual == fake_definition

        thisid = 789012
        url = group.api.compute_url('%s/suspend' % thisid)
        with requests_mock.Mocker() as m:
            m.post(url, json=expected)
            actual = group.suspend(uuid=thisid)
            assert actual == expected

        thisid = 345678
        url = group.api.compute_url('%s/activate' % thisid)
        with requests_mock.Mocker() as m:
            m.post(url, json=expected)
            actual = group.activate(uuid=thisid)
            assert actual == expected

        thisid = 901234
        url = group.api.compute_url('%s/terminate' % thisid)
        with requests_mock.Mocker() as m:
            m.post(url, json=expected)
            actual = group.terminate(uuid=thisid)
            assert actual == expected
