#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# globalconfig.py
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


class GlobalConfig(ORapi):
    def __init__(self, parent):
        super(GlobalConfig, self).__init__(parent.api, '')

    def get_alert_types(self):
        return self.api.get('/alertTypes')

    def get_countries(self):
        return self.api.get('/cfg/countries')

    def get_timezones(self):
        return self.api.get('/cfg/timezones')

    def get_alert_technologies(self):
        return self.api.get('/cfg/alertTechnologies')

    def get_channels(self):
        return self.api.get('/cfg/tenants/channels')

    def get_nocs(self):
        # Bizarrely this API call throws a 500 error if there are
        # no NOCs defined. Handle it gracefully.
        try:
            retval = self.api.get('/cfg/tenants/nocs')
        except RuntimeError as e:
            if '"code":"0005"' in str(e):
                retval = []
            else:
                raise
        return retval

    def get_device_types(self):
        return self.api.get('/cfg/devices/types')
