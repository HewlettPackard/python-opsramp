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
