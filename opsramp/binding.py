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


class Monitoring(ApiWrapper):
    def __init__(self, parent):
        super(Monitoring, self).__init__(parent.api, 'monitoring')

    def templates(self):
        return Templates(self)


class Templates(ApiWrapper):
    def __init__(self, parent):
        super(Templates, self).__init__(parent.api, 'templates')

    def search(self, pattern=''):
        suffix = '/search'
        if pattern:
            suffix += '?' + pattern
        return self.api.get(suffix)


class Clients(ApiWrapper):
    def __init__(self, parent):
        super(Clients, self).__init__(parent.api, 'clients')

    def get_list(self):
        return self.api.get('/minimal')

    def client(self, uuid):
        return Client(self, uuid)

    def create_client(self, client_definition):
        return self.api.post('', json=client_definition)


class Client(ApiWrapper):
    def __init__(self, parent, uuid):
        assert uuid[:7] == 'client_'
        super(Client, self).__init__(parent.api, '%s' % uuid)

    def get(self):
        return self.api.get()


class Policies(ApiWrapper):
    def __init__(self, parent):
        super(Policies, self).__init__(parent.api, 'policies/management')

    def get_list(self):
        return self.api.get()

    def search(self, pattern=''):
        return self.api.get('/search?name=%s' % pattern)

    def policy(self, uuid):
        return Policy(self, uuid)

    def create_policy(self, policy_definition):
        return self.api.post('', json=policy_definition)

    def update_policy(self, policy_definition):
        return self.api.put('', json=policy_definition)


class Policy(ApiWrapper):
    def __init__(self, parent, uuid):
        super(Policy, self).__init__(parent.api, '%s' % uuid)

    def get(self):
        return self.api.get()

    def run(self):
        return self.api.get('/action/run')

    def delete(self):
        return self.api.delete()
