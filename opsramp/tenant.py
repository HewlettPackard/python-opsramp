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
import opsramp.resources


class Tenant(ApiWrapper):
    def __init__(self, parent, uuid):
        super(Tenant, self).__init__(parent.api, 'tenants/%s' % uuid)
        self.uuid = uuid

    def is_client(self):
        return self.uuid[:7] == 'client_'

    def rba(self):
        if not hasattr(self, 'rba_object'):
            self.rba_object = opsramp.rba.Rba(self)
        return self.rba_object

    def monitoring(self):
        if not hasattr(self, 'monitoring_object'):
            self.monitoring_object = opsramp.monitoring.Monitoring(self)
        return self.monitoring_object

    def clients(self):
        assert not self.is_client()
        if not hasattr(self, 'clients_object'):
            self.clients_object = opsramp.msp.Clients(self)
        return self.clients_object

    def policies(self):
        if not hasattr(self, 'policies_object'):
            self.policies_object = opsramp.devmgmt.Policies(self)
        return self.policies_object

    def discovery(self):
        if not hasattr(self, 'discovery_object'):
            self.discovery_object = opsramp.devmgmt.Discovery(self)
        return self.discovery_object

    def integrations(self):
        if not hasattr(self, 'integrations_object'):
            self.integrations_object = opsramp.integrations.Integrations(self)
        return self.integrations_object

    def get_agent_script(self):
        assert self.is_client()
        hdr = {'Accept': 'application/octet-stream,application/xml'}
        return self.api.get('agents/deployAgentsScript', headers=hdr)

    def credential_sets(self):
        if not hasattr(self, 'cred_sets_object'):
            self.cred_sets_object = opsramp.devmgmt.CredentialSets(self)
        return self.cred_sets_object

    def resources(self):
        if not hasattr(self, 'resources_object'):
            self.resources_object = opsramp.resources.Resources(self)
        return self.resources_object

    def roles(self):
        if not hasattr(self, 'roles_object'):
            self.roles_object = opsramp.roles.Roles(self)
        return self.roles_object

    def permission_sets(self):
        if not hasattr(self, 'perm_sets_object'):
            self.perm_sets_object = opsramp.roles.PermissionSets(self)
        return self.perm_sets_object

    def escalations(self):
        if not hasattr(self, 'escalations_object'):
            self.escalations_object = opsramp.escalations.Escalations(self)
        return self.escalations_object

    def mgmt_profiles(self):
        if not hasattr(self, 'dmps_object'):
            self.dmps_object = opsramp.mgmt_profiles.Profiles(self)
        return self.dmps_object

    def sites(self):
        if not hasattr(self, 'sites_object'):
            self.sites_object = opsramp.sites.Sites(self)
        return self.sites_object

    def service_maps(self):
        if not hasattr(self, 'service_maps_object'):
            self.service_maps_object = opsramp.service_maps.ServiceMaps(self)
        return self.service_maps_object

    def kb(self):
        if not hasattr(self, 'kb_object'):
            self.kb_object = opsramp.kb.KnowledgeBase(self)
        return self.kb_object
