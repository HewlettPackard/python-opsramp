#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# msp.py
# Classes related to partner-level actions.
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
import datetime
from opsramp.base import ApiWrapper


class Clients(ApiWrapper):
    def __init__(self, parent):
        super(Clients, self).__init__(parent.api, 'clients')

    def get_list(self):
        return self.api.get('/minimal')

    def search(self, pattern=''):
        return self.api.get('/search?%s' % pattern)

    def search_for_prefix(self, prefix):
        return self.api.get('/search?queryString=name:%s' % prefix)

    def create_client(self, definition):
        assert 'name' in definition
        assert 'address' in definition
        assert 'timeZone' in definition
        assert 'country' in definition
        return self.api.post('', json=definition)

    def client(self, uuid):
        return Client(self, uuid)


class Client(ApiWrapper):
    def __init__(self, parent, uuid):
        assert uuid[:7] == 'client_'
        super(Client, self).__init__(parent.api, '%s' % uuid)

    @staticmethod
    def mkhours(day_start=datetime.time(9, 0),
                day_end=datetime.time(17, 0),
                week_start=2, week_end=6,
                sms_voice_notification=False):
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
    def mkclient(name, address, time_zone, country,
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

    def activate(self):
        return self.api.post('/activate')

    def suspend(self):
        return self.api.post('/suspend')

    def terminate(self):
        return self.api.post('/terminate')

    def update(self, definition):
        return self.api.post(json=definition)
