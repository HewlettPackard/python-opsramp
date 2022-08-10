#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# resources.py
# Resource classes.
#
# (c) Copyright 2019-2022 Hewlett Packard Enterprise Development LP
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

from opsramp.api import ORapi
from opsramp.resources import list2ormp


class ResourceGroups(ORapi):
    def __init__(self, parent):
        super(ResourceGroups, self).__init__(parent.api, "deviceGroups")

    def get(self):
        temp_url = "/search"
        return self.api.get(temp_url)

    def create(self, definition):
        url_suffix = ""
        return self.api.post(url_suffix, json=definition)

    def update(self, definition):
        # UUID(s) specified in the request body(ies).
        return self.api.post(json=definition)

    def delete(self, uuid):
        url_suffix = uuid
        return self.api.delete(url_suffix)

    def search(self, pattern=""):
        """returns *verbose* details about resource groups on this tenant"""
        simple_list = super(ResourceGroups, self).search(
            pattern=pattern, suffix="search"
        )
        return list2ormp(simple_list)

    def minimal(self, pattern=""):
        """returns * minimal * details about resource groups on this tenant"""
        simple_list = super(ResourceGroups, self).search(
            pattern=pattern, suffix="minimal"
        )
        return list2ormp(simple_list)
