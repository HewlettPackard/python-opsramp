#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# resources.py
# Classes related to resources
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


class Resources(ApiWrapper):
    def __init__(self, parent, uuid):
        super(Resources, self).__init__(parent.api, '')
        self.uuid = uuid

    def get(self, resource):
        suffix = '/tenants/%s/resources/%s' % \
                 (self.uuid, resource)
        return self.api.get(suffix)

    def search(self):
        suffix = '/tenants/%s/resources/search?queryString=Id' % \
            self.uuid
        return self.api.get(suffix)
