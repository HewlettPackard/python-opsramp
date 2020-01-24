#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# sites.py
# Classes dealing directly with OpsRamp Service Maps.
# Service Maps are used to organise resources by any method and
# create availability rules governing how they show problems.
#
# (c) Copyright 2020 Hewlett Packard Enterprise Development LP
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


class ServiceMaps(ApiWrapper):
    def __init__(self, parent):
        super(ServiceMaps, self).__init__(parent.api, 'serviceGroups')

    def get(self, uuid=False, minimal=False):
        if uuid:
            temp_url = '/%s/childs/search' % uuid
        else:
            temp_url = '/search'
        if minimal:
            temp_url = '/minimal'
        return self.api.get(temp_url)

    def create(self, definition):
        return self.api.post('', json=definition)

    def update(self, uuid, definition):
        return self.api.post('%s' % uuid, json=definition)

    def delete(self, uuid):
        return self.api.delete('%s' % uuid)
