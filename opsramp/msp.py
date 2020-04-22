#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# msp.py
# Classes related to partner-level actions.
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
import datetime
from opsramp.base import ApiWrapper


class Clients(ApiWrapper):
    def __init__(self, parent):
        super(Clients, self).__init__(parent.api, 'clients')

    def get(self, suffix='/minimal'):
        return self.api.get(suffix)

    def search(self, pattern=''):
        path = '/search'
        if pattern:
            path += '?queryString=' + pattern
        return self.api.get(path)

    def create(self, definition):
        assert 'name' in definition
        assert 'address' in definition
        assert 'timeZone' in definition
        assert 'country' in definition
        return self.api.post('', json=definition)

    def update(self, uuid, definition):
        return self.api.post('%s' % uuid, json=definition)

    def activate(self, uuid):
        return self.api.post('%s/activate' % uuid)

    def suspend(self, uuid):
        return self.api.post('%s/suspend' % uuid)

    def terminate(self, uuid):
        return self.api.post('%s/terminate' % uuid)

    # Helper functions to create the complex structures that OpsRamp
    # uses to manipulate client definitions.
    @staticmethod
    def mkHours(day_start=None,
                day_end=None,
                week_start=2, week_end=6,
                sms_voice_notification=False):
        if not day_start:
            day_start = datetime.time(9, 0)
        if not day_end:
            day_end = datetime.time(17, 0)
        retval = {
            'businessStartHour': day_start.hour,
            'businessStartMin': day_start.minute,
            'businessEndHour': day_end.hour,
            'businessEndMin': day_end.minute,
            'businessDayStart': int(week_start),
            'businessDayEnd': int(week_end),
            'smsVoiceNotification': bool(sms_voice_notification)
        }
        return retval

    # A helper function to create the complex structures that OpsRamp
    # uses to define a new client. There are lots of optional fields and
    # potential gotchas here and we guard against *some* of them.
    @staticmethod
    def mkClient(name, address, time_zone, country,
                 hours=None):
        retval = {
            'name': name,
            'address': address,
            'timeZone': time_zone,
            'country': country
        }
        if hours:
            retval['clientDetails'] = hours
        # TODO there are lots and lots more optional fields that we
        # will probably need to cater for in the fullness of time.
        return retval
