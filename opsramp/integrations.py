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
import os
from opsramp.base import ApiWrapper, Helpers

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
        resp = self.api.post('install/%s' % type_name, json=definition)
        return resp

    def instance(self, uuid):
        return SingleInstance(self, uuid)

    # Helper functions to create the complex structures that OpsRamp
    # uses to define new integration instances. There are lots of
    # optional fields and potential gotchas here and we guard against
    # *some* of them.
    @staticmethod
    def mkBase(display_name,
               logo_fname=None):
        retval = {
            'displayName': display_name,
        }
        if logo_fname:
            payload = Helpers.b64encode_payload(logo_fname)
            retval['logo'] = {
                'name': os.path.basename(logo_fname),
                'file': payload
            }
        return retval

    @staticmethod
    def mkEmailAlert(display_name,
                     logo_fname=None):
        retval = Integrations.mkBase(display_name, logo_fname)
        return retval

    @staticmethod
    def mkCustom(display_name,
                 logo_fname=None,
                 parent_uuid=None,
                 inbound_auth_type=None):
        retval = Integrations.mkBase(display_name, logo_fname)
        if parent_uuid:
            retval['parentIntg'] = {
                'id': parent_uuid
            }
        if inbound_auth_type:
            assert inbound_auth_type in ('OAUTH2', 'BASIC')
            retval['inboundConfig'] = {
                'authentication': {
                    'authType': inbound_auth_type
                }
            }
        return retval

    @staticmethod
    def mkAzureARM(display_name,
                   arm_subscription_id,
                   arm_tenant_id,
                   arm_client_id,
                   arm_secret_key):
        retval = {
            'displayName': display_name,
            'credential': {
                'credentialType': 'AZURE',
                'AzureType': 'ARM',
                'SubscriptionId': arm_subscription_id,
                'TenantId': arm_tenant_id,
                'ClientID': arm_client_id,
                'SecretKey': arm_secret_key
            }
        }
        return retval

    @staticmethod
    def mkAzureASM(display_name,
                   arm_subscription_id,
                   arm_mgmt_cert,
                   arm_keystore_pass):
        retval = {
            'displayName': display_name,
            'credential': {
                'credentialType': 'AZURE',
                'AzureType': 'ASM',
                'SubscriptionId': arm_subscription_id,
                'ManagementCertificate': arm_mgmt_cert,
                'KeystorePassword': arm_keystore_pass
            }
        }
        return retval

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

    def search(self, pattern=''):
        suffix = '/search'
        if pattern:
            suffix += '?' + pattern
        return self.api.get(suffix)


class SingleInstance(ApiWrapper):
    def __init__(self, parent, uuid):
        api = parent.api.clone()
        api.chroot('/installed')
        super(SingleInstance, self).__init__(api, uuid)

    def enable(self):
        return self.api.post('/enable')

    def disable(self):
        return self.api.post('/disable')

    def notifier(self, definition):
        return self.api.post('/notifier', json=definition)

    def update(self, definition):
        return self.api.post(json=definition)

    def set_auth_type(self, auth_type):
        assert auth_type in ('OAUTH2', 'WEBHOOK', 'BASIC')
        settings = {
            'authType': auth_type
        }
        return self.api.post('inbound/authentication', json=settings)
