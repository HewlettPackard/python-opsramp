#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# binding.py
# Defines the primary entry points for callers of this library.
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

from opsramp.base import ApiObject, ApiWrapper
from opsramp.globalconfig import GlobalConfig
from opsramp.rba import Rba
from opsramp.monitoring import Monitoring
from opsramp.msp import Clients
from opsramp.devmgmt import Policies


def connect(url, key, secret):
    auth_url = url + '/auth/oauth/token'
    auth_hdrs = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json,application/xml'
    }
    body = 'grant_type=client_credentials&' \
           'client_id=%s&' \
           'client_secret=%s' % (key, secret)
    ao = ApiObject(auth_url, auth_hdrs)
    auth_resp = ao.post(data=body)
    token = auth_resp['access_token']
    return Opsramp(url, token)


class Opsramp(ApiWrapper):
    def __init__(self, url, token):
        self.auth = {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json,application/xml'
        }
        apiobject = ApiObject(url + '/api/v2', self.auth)
        super(Opsramp, self).__init__(apiobject)

    def __str__(self):
        return '%s %s' % (str(type(self)), self.api)

    def config(self):
        return GlobalConfig(self)

    def tenant(self, name):
        return Tenant(self, name)


class Tenant(ApiWrapper):
    def __init__(self, parent, uuid):
        super(Tenant, self).__init__(parent.api, 'tenants/%s' % uuid)
        self.uuid = uuid

    def is_client(self):
        return self.uuid[:7] == 'client_'

    def rba(self):
        return Rba(self)

    def monitoring(self):
        return Monitoring(self)

    def clients(self):
        assert not self.is_client()
        return Clients(self)

    def get_alerts(self, searchpattern):
        return self.api.get('/alerts/search?queryString=%s' % searchpattern)

    def get_agent_script(self):
        assert self.is_client()
        hdr = {'Accept': 'application/octet-stream,application/xml'}
        return self.api.get('agents/deployAgentsScript', headers=hdr)

    def policies(self):
        return Policies(self)
