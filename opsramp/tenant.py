#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# tenant.py
# Classes dealing directly with OpsRamp Tenants.
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

from opsramp.base import ApiWrapper
import opsramp.rba
import opsramp.monitoring
import opsramp.msp
import opsramp.devmgmt
import opsramp.integrations
import opsramp.roles
import opsramp.escalations
import opsramp.mgmt_profiles
import opsramp.sites
import opsramp.service_maps
import opsramp.kb


class Tenant(ApiWrapper):
    def __init__(self, parent, uuid):
        super(Tenant, self).__init__(parent.api, 'tenants/%s' % uuid)
        self.uuid = uuid

    def is_client(self):
        return self.uuid[:7] == 'client_'

    def rba(self):
        return opsramp.rba.Rba(self)

    def monitoring(self):
        return opsramp.monitoring.Monitoring(self)

    def clients(self):
        assert not self.is_client()
        return opsramp.msp.Clients(self)

    def policies(self):
        return opsramp.devmgmt.Policies(self)

    def discovery(self):
        return opsramp.devmgmt.Discovery(self)

    def integrations(self):
        return opsramp.integrations.Integrations(self)

    def get_agent_script(self):
        assert self.is_client()
        hdr = {'Accept': 'application/octet-stream,application/xml'}
        return self.api.get('agents/deployAgentsScript', headers=hdr)

    def credential_sets(self):
        return opsramp.devmgmt.CredentialSets(self)

    def roles(self):
        return opsramp.roles.Roles(self)

    def permission_sets(self):
        return opsramp.roles.PermissionSets(self)

    def escalations(self):
        return opsramp.escalations.Escalations(self)

    def mgmt_profiles(self):
        return opsramp.mgmt_profiles.Profiles(self)

    def sites(self):
        return opsramp.sites.Sites(self)

    def service_maps(self):
        return opsramp.service_maps.ServiceMaps(self)

    def kb(self):
        return opsramp.kb.KnowledgeBase(self)
