#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# devmgmt.py
# Device management classes.
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
from opsramp.base import ApiWrapper


class Policies(ApiWrapper):
    def __init__(self, parent):
        super(Policies, self).__init__(parent.api, 'policies/management')

    def search(self, pattern=''):
        return self.api.get('/search?name=%s' % pattern)

    def create(self, definition):
        return self.api.post('', json=definition)

    def update(self, uuid, definition):
        return self.api.put('%s' % uuid, json=definition)

    def run(self, uuid):
        return self.api.get('%s/action/run' % uuid)

    def delete(self, uuid):
        return self.api.delete('%s' % uuid)


class Discovery(ApiWrapper):
    def __init__(self, parent):
        assert parent.is_client()
        super(Discovery, self).__init__(parent.api, 'policies/discovery')

    def search(self, pattern=''):
        return self.api.get('/search?name=%s' % pattern)

    def create(self, definition):
        return self.api.post('', json=definition)

    def update(self, definition):
        return self.api.post('', json=definition)

    def rescan(self, discoveryProfileId):
        return self.api.get('/action/scan/%s' % discoveryProfileId)

    def delete(self, discoveryProfileId):
        return self.api.delete('/%s' % discoveryProfileId)


class CredentialSets(ApiWrapper):
    def __init__(self, parent):
        super(CredentialSets, self).__init__(parent.api, 'credentialSets')

    def get(self, credentialSetId='', minimal=False):
        if minimal:
            return self.api.get('/%s/minimal' % credentialSetId)
        else:
            return self.api.get('/%s' % credentialSetId)

    def create(self, definition):
        return self.api.post('', json=definition)

    def update(self, credentialSetId, definition):
        return self.api.post('/%s' % credentialSetId, json=definition)

    def delete(self, credentialSetId):
        return self.api.delete('/%s' % credentialSetId)
