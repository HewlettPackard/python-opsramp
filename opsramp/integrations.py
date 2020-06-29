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
GET installed/{installedIntgld}/configFile/kubernetes
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

    def itypes(self):
        return Types(self)

    def instances(self):
        return Instances(self)

    def available(self):
        # Compatibility function because this is the name that the
        # OpsRamp API docs use for this data set.
        return self.itypes()

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
        # The OpsRamp "create instance" API endpoint is in an
        # atypical place in the tree so need to compute it.
        self.creator_api = parent.api.clone()
        self.creator_api.chroot('install')

    def search(self, pattern=''):
        suffix = '/search'
        if pattern:
            suffix += '?' + pattern
        return self.api.get(suffix)

    def get_kubernetes_configuration(self, uuid):
        return self.api.get('%s/configFile/kubernetes' % uuid)

    def create(self, type_name, definition):
        resp = self.creator_api.post(type_name, json=definition)
        return resp

    def update(self, uuid, definition):
        return self.api.post('%s' % uuid, json=definition)

    def set_auth_type(self, uuid, auth_type):
        assert auth_type in ('OAUTH2', 'WEBHOOK', 'BASIC')
        settings = {
            'authType': auth_type
        }
        return self.api.post('%s/inbound/authentication' % uuid, json=settings)

    def enable(self, uuid):
        return self.api.post('%s/enable' % uuid)

    def disable(self, uuid):
        return self.api.post('%s/disable' % uuid)

    def notifier(self, uuid, definition):
        return self.api.post('%s/notifier' % uuid, json=definition)

    # A helper function that extracts the authentication types from typical
    # integration instance response structs.
    @staticmethod
    def auth_type(resp):
        in_auth = resp.get(
            'inboundConfig', {}).get(
                'authentication', {}).get(
                    'authType', None)
        out_auth = resp.get(
            'outboundConfig', {}).get(
                'authentication', {}).get(
                    'authType', None)
        return (in_auth, out_auth)

    # A helper function that looks for login credentials in typical
    # integration instance response structs and redacts them.
    @staticmethod
    def redact_response(resp):
        for key in ('inboundConfig', 'outboundConfig'):
            config = resp.get(key, {})
            auth = config.get('authentication', {})
            if 'token' in auth:
                auth['token'] = 'REDACTED'
            for creds in auth.get('apiKeyPairs', {}):
                for i in creds.keys():
                    creds[i] = 'REDACTED'
        return resp

    # Helper functions to create the complex structures that OpsRamp
    # uses to define new integration instances. There are lots of
    # optional fields and potential gotchas here and we guard against
    # *some* of them.
    @staticmethod
    def mkBase(display_name,
               logo_fname=None):
        assert display_name
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
        assert display_name
        retval = Instances.mkBase(display_name, logo_fname)
        return retval

    @staticmethod
    def mkCustom(display_name,
                 logo_fname=None,
                 parent_uuid=None,
                 inbound_auth_type=None):
        assert display_name
        retval = Instances.mkBase(display_name, logo_fname)
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
        assert display_name
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
        assert display_name
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

    @staticmethod
    def mkBaseNotifier(api_type, base_uri,
                       auth_type='OAUTH2',
                       grant_type='CLIENT_CREDENTIALS',
                       access_token_uri=None,
                       api_key=None,
                       api_secret=None,
                       user_name=None,
                       password=None):
        assert api_type in ('REST_API', 'SOAP_API')
        assert base_uri
        assert auth_type in ('NONE', 'BASIC', 'OAUTH2')
        retval = {
            'type': api_type,
            'baseURI': base_uri,
            'authType': auth_type
        }
        if auth_type != 'NONE':
            retval['grantType'] = grant_type
            if auth_type == 'OAUTH2':
                assert grant_type in ('CLIENT_CREDENTIALS', 'PASSWORD')
                # empty string is ok but omitting these isn't.
                assert access_token_uri is not None
                assert api_key is not None
                assert api_secret is not None
                retval['accessTokenURI'] = access_token_uri
                retval['apiKey'] = api_key
                retval['apiSecret'] = api_secret
            if grant_type == 'PASSWORD':
                # empty string is ok but omitting these isn't.
                assert user_name is not None
                assert password is not None
                retval['userName'] = user_name
                retval['password'] = password
        return retval

    # mkValueMap(('attrValue', 'tenantAttrValue'),
    #            (('client_113', '22cdbc5bb401d737b088c9'),
    #             ('client_843', '66cdbc5bb401d737b088c9'))
    @staticmethod
    def mkValueMap(labels, value_pairs):
        ormpname, othername = labels
        retval = [{ormpname: x[0], othername: x[1]} for x in value_pairs]
        return retval
