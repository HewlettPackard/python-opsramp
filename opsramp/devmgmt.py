#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# devmgmt.py
# Device management classes.
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
from opsramp.api import ORapi


class Policies(ORapi):
    def __init__(self, parent):
        super(Policies, self).__init__(parent.api, 'policies/management')

    def search(self, policy_name=''):
        '''For historical reasons this class's search function might be
        called with just a name. We have to cope and convert it into a
        proper query string.'''
        if policy_name and '=' not in policy_name:
            qstring = 'name=' + policy_name
        else:
            qstring = policy_name
        # we have assembled a proper query string now so use regular search.
        return super(Policies, self).search(pattern=qstring)

    def create(self, definition):
        return self.api.post('', json=definition)

    def update(self, uuid, definition):
        return self.api.put('%s' % uuid, json=definition)

    def run(self, uuid):
        return self.api.get('%s/action/run' % uuid)

    def delete(self, uuid):
        return self.api.delete('%s' % uuid)


class Discovery(ORapi):
    def __init__(self, parent):
        assert parent.is_client()
        super(Discovery, self).__init__(parent.api, 'policies/discovery')

    def search(self, profile_name=''):
        '''For historical reasons this class's search function might be
        called with just a name. We have to cope and convert it into a
        proper query string.'''
        if profile_name and '=' not in profile_name:
            qstring = 'name=' + profile_name
        else:
            qstring = profile_name
        # we have assembled a proper query string now so use regular search.
        return super(Discovery, self).search(pattern=qstring)

    def create(self, definition):
        return self.api.post('', json=definition)

    def update(self, definition):
        return self.api.post('', json=definition)

    def rescan(self, uuid):
        return self.api.get('/action/scan/%s' % uuid)

    def delete(self, uuid):
        return self.api.delete('/%s' % uuid)


class CredentialSets(ORapi):
    def __init__(self, parent):
        super(CredentialSets, self).__init__(parent.api, 'credentialSets')

    def get(self, uuid='', minimal=False):
        if minimal:
            return self.api.get('/%s/minimal' % uuid)
        else:
            return self.api.get('/%s' % uuid)

    def create(self, definition):
        return self.api.post('', json=definition)

    def update(self, uuid, definition):
        return self.api.post('/%s' % uuid, json=definition)

    def delete(self, uuid):
        return self.api.delete('/%s' % uuid)
