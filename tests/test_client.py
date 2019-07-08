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

from opsramp.msp import Clients


class ClientsTest(unittest.TestCase):
    def test_mkhours(self):
        tvalues = {
            'start_hour': 10,
            'start_min': 40,
            'end_hour': 19,
            'end_min': 23,
            'week_start': 1,
            'week_end': 4,
            'sms_voice_notifications': True
        }
        actual = Clients.mkhours(
            day_start=datetime.time(
                tvalues['start_hour'], tvalues['start_min']),
            day_end=datetime.time(
                tvalues['end_hour'], tvalues['end_min']),
            week_start=tvalues['week_start'],
            week_end=tvalues['week_end'],
            sms_voice_notification=tvalues['sms_voice_notifications']
        )
        expected = {
            'businessStartHour': tvalues['start_hour'],
            'businessStartMin': tvalues['start_min'],
            'businessEndHour': tvalues['end_hour'],
            'businessEndMin': tvalues['end_min'],
            'businessDayStart': tvalues['week_start'],
            'businessDayEnd': tvalues['week_end'],
            'smsVoiceNotification': tvalues['sms_voice_notifications']
        }
        assert actual == expected

    def test_mkclient(self):
        tvalues = {
            'name': 'unit test client',
            'address': 'Springfield',
            'tz': 'America/Los_Angeles',
            'country': 'United States'
        }
        actual = Clients.mkclient(
            name=tvalues['name'],
            address=tvalues['address'],
            time_zone=tvalues['tz'],
            country=tvalues['country'],
        )
        expected = {
            'name': tvalues['name'],
            'address': tvalues['address'],
            'timeZone': tvalues['tz'],
            'country': tvalues['country']
        }
        assert actual == expected
