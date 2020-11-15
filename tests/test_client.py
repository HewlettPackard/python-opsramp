#!/usr/bin/env python
#
# (c) Copyright 2019-2020 Hewlett Packard Enterprise Development LP
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

        self.fake_msp_id = 'msp_123456'
        self.msp = self.ormp.tenant(self.fake_msp_id)
        assert not self.msp.is_client()

        self.clients = self.msp.clients()
        assert self.clients

    def test_search(self):
        thisid = 444444
        expected = {'id': thisid}
        url = self.clients.api.compute_url('search?queryString=id:%s' % thisid)
        with requests_mock.Mocker() as m:
            m.get(url, json=expected, complete_qs=True)
            actual = self.clients.search('id:%s' % thisid)
            assert actual == expected

    def test_minimal(self):
        thisid = 555555
        expected = {'id': thisid}
        url = self.clients.api.compute_url('minimal')
        with requests_mock.Mocker() as m:
            m.get(url, json=expected, complete_qs=True)
            # specific suffix.
            actual = self.clients.get('minimal')
            assert actual == expected
            # default suffix should be the same.
            actual = self.clients.get()
            assert actual == expected

    def test_create_update(self):
        bad_definition = {'bogus': 'dude'}
        with requests_mock.Mocker() as m:
            # the name field is missing so we should get an error.
            assert 'name' not in bad_definition
            with self.assertRaises(AssertionError):
                actual = self.clients.create(definition=bad_definition)
            assert m.call_count == 0
        # now let's try a valid one.
        good_definition = {
            'name': 'elvis',
            'address': 'graceland',
            'timeZone': 'UTC',
            'country': 'US'
        }
        thisid = 555555
        expected_send = good_definition
        expected_receive = {'id': thisid}
        url = self.clients.api.compute_url()
        with requests_mock.Mocker() as m:
            adapter = m.post(url, json=expected_receive, complete_qs=True)
            actual = self.clients.create(definition=good_definition)
            assert adapter.last_request.json() == expected_send
            assert actual == expected_receive
        # now try update
        url = self.clients.api.compute_url(thisid)
        with requests_mock.Mocker() as m:
            adapter = m.post(url, json=expected_receive, complete_qs=True)
            actual = self.clients.update(
                uuid=thisid,
                definition=good_definition
            )
            assert adapter.last_request.json() == expected_send
            assert actual == expected_receive

    def test_suspend(self):
        thisid = 789012
        expected = {'id': thisid}
        url = self.clients.api.compute_url('%s/suspend' % thisid)
        with requests_mock.Mocker() as m:
            m.post(url, json=expected, complete_qs=True)
            actual = self.clients.suspend(uuid=thisid)
            assert actual == expected

    def test_activate(self):
        thisid = 345678
        expected = {'id': thisid}
        url = self.clients.api.compute_url('%s/activate' % thisid)
        with requests_mock.Mocker() as m:
            m.post(url, json=expected, complete_qs=True)
            actual = self.clients.activate(uuid=thisid)
            assert actual == expected

    def test_terminate(self):
        thisid = 901234
        expected = {'id': thisid}
        url = self.clients.api.compute_url('%s/terminate' % thisid)
        with requests_mock.Mocker() as m:
            m.post(url, json=expected, complete_qs=True)
            actual = self.clients.terminate(uuid=thisid)
            assert actual == expected
