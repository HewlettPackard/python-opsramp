#!/usr/bin/env python
#
# A Python language binding for the OpsRamp REST API.
#
# integrations.py
# Classes related to Integrations.
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

'''
POST install/{intgld} e.g. CUSTOM

GET installed/search?queryString=
GET installed/{installedIntgld}
DELETE installed/{installedIntgld}
POST installed/{installedIntgld}
POST installed/{installedIntgld}/notifier
POST installed/{installedIntgld}/enable
POST installed/{installedIntgld}/disable
POST installed/{installedIntgld}/inbound/authentication
POST installed/{installedIntgld}/mappingAttr

GET available/search?queryString=
GET available/{intgld}/emailProps/{entityType}
GET available/{intgld}/mappingAttr/{entityType}
'''


class Integrations(ApiWrapper):
    def __init__(self, parent):
        super(Integrations, self).__init__(parent.api, 'integrations')

    def types(self):
        return Types(self)

    def instances(self):
        return Instances(self)

    def create_instance(self, type_name, definition):
        resp = self.api.post('install', type_name, json=definition)
        return resp

    def available(self):
        # Compatibility function because this is the name that the
        # OpsRamp API docs use for this data set.
        return self.types()

    def installed(self):
        # Compatibility function because this is the name that the
        # OpsRamp API docs use for this data set.
        return self.instances()


class Types(ApiWrapper):
    def __init__(self, parent):
        super(Types, self).__init__(parent.api, 'available')

    def search(self, pattern=''):
        suffix = '/search'
        if pattern:
            suffix += '?' + pattern
        return self.api.get(suffix)


class Instances(ApiWrapper):
    def __init__(self, parent):
        super(Instances, self).__init__(parent.api, 'installed')

    def instance(self, uuid):
        return SingleInstance(self, uuid)

    def search(self, pattern=''):
        suffix = '/search'
        if pattern:
            suffix += '?' + pattern
        return self.api.get(suffix)


class SingleInstance(ApiWrapper):
    def __init__(self, parent, uuid):
        super(SingleInstance, self).__init__(parent.api, uuid)

    def enable(self):
        return self.api.post('/enable')

    def disable(self):
        return self.api.post('/disable')

    def notifier(self, definition):
        return self.api.post('/notifier', json=definition)
