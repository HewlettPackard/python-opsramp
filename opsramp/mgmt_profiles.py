#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# mgmt_profiles.py
# Classes dealing directly with OpsRamp Management Profiles.
# The are used for interactions with gateway nodes.
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


class Profiles(ORapi):
    def __init__(self, parent):
        super(Profiles, self).__init__(parent.api, 'managementProfiles')

    def create(self, definition):
        return self.api.post('', json=definition)

    def update(self, uuid, definition):
        return self.api.post('%s' % uuid, json=definition)

    def delete(self, uuid):
        return self.api.delete('%s' % uuid)

    def attach(self, uuid):
        return self.api.get('%s/attach' % uuid)

    def detach(self, uuid):
        return self.api.get('%s/detach' % uuid)

    def reconnect(self, uuid):
        return self.api.get('%s/reconnectTunnel' % uuid)
