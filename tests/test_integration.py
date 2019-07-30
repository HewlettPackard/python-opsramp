#!/usr/bin/env python
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
import base64
import copy
import unittest

from opsramp.integrations import Instances


class InstancesTest(unittest.TestCase):
    def base_display_name(self, fn):
        with self.assertRaises(AssertionError):
            fn(display_name=None)
        testname = 'Unit test 1'
        actual = fn(display_name=testname)
        expected = {
            'displayName': testname
        }
        assert actual == expected

    def base_logo(self, fn):
        testname = 'Unit test 2'
        testfile = 'README.md'
        with self.assertRaises(IOError):
            fn(
                display_name=testname,
                logo_fname=testfile + '.that.doesnt.exist'
            )
        actual = fn(
            display_name=testname,
            logo_fname=testfile
        )
        encoded = actual['logo']['file']
        cleartext = base64.b64decode(encoded)
        with open(testfile, 'rb') as f:
            content = f.read()
        assert content == cleartext

        expected = {
            'displayName': testname,
            'logo': {
                'name': testfile,
                'file': encoded
            }
        }
        assert actual == expected

    def test_base(self):
        self.base_display_name(Instances.mkBase)
        self.base_logo(Instances.mkBase)

    def test_emailalert(self):
        self.base_display_name(Instances.mkEmailAlert)
        self.base_logo(Instances.mkEmailAlert)

    def test_custom(self):
        self.base_display_name(Instances.mkCustom)
        self.base_logo(Instances.mkCustom)
        with self.assertRaises(AssertionError):
            Instances.mkCustom(
                display_name='bad auth type',
                inbound_auth_type='BAD UNIT TEST VALUE'
            )
        # Now a variant that should work.
        testname = 'Custom integration unit test'
        fakeuuid = 'deadbeef'
        auth_type = 'OAUTH2'
        actual = Instances.mkCustom(
            display_name=testname,
            parent_uuid=fakeuuid,
            inbound_auth_type=auth_type
        )
        expected = {
            'displayName': testname,
            'parentIntg': {
                'id': fakeuuid
            },
            'inboundConfig': {
                'authentication': {'authType': auth_type}
            }
        }
        assert actual == expected
        # exercise the auth_type helper while we have a suitable struct.
        atypes = Instances.auth_type(actual)
        assert atypes == (auth_type, None)

    def test_ARM(self):
        testname = 'Azure ARM integration unit test'
        subscription_id = '123456789'
        tenant_id = 'Some random Azure tenant'
        client_id = 'Azure client shtuff'
        secret_key = 'Open Sesame I Say!'
        actual = Instances.mkAzureARM(
            display_name=testname,
            arm_subscription_id=subscription_id,
            arm_tenant_id=tenant_id,
            arm_client_id=client_id,
            arm_secret_key=secret_key
        )
        expected = {
            'displayName': testname,
            'credential': {
                'credentialType': 'AZURE',
                'AzureType': 'ARM',
                'SubscriptionId': subscription_id,
                'TenantId': tenant_id,
                'ClientID': client_id,
                'SecretKey': secret_key
            }
        }
        assert actual == expected

    def test_ASM(self):
        testname = 'Azure ASM integration unit test'
        subscription_id = 'ABCDEFGHIJKLMNOP'
        mgmt_cert = 'Azure management cert'
        keystore_pass = 'Abrakedabra'
        actual = Instances.mkAzureASM(
            display_name=testname,
            arm_subscription_id=subscription_id,
            arm_mgmt_cert=mgmt_cert,
            arm_keystore_pass=keystore_pass
        )
        expected = {
            'displayName': testname,
            'credential': {
                'credentialType': 'AZURE',
                'AzureType': 'ASM',
                'SubscriptionId': subscription_id,
                'ManagementCertificate': mgmt_cert,
                'KeystorePassword': keystore_pass
            }
        }
        assert actual == expected

    def test_basenotifier(self):
        expected = {
            'type': 'REST_API',
            'baseURI': 'www.example.com',
            'authType': 'OAUTH2',
            'grantType': 'CLIENT_CREDENTIALS',
            'accessTokenURI': 'www.example.com/creds',
            'apiKey': '6h67PAAFscVPMwhQZFcshpcqN5b6pyU9',
            'apiSecret': 'totalandcompletenonsense'
        }
        actual = Instances.mkBaseNotifier(
            expected['type'], expected['baseURI'],
            access_token_uri=expected['accessTokenURI'],
            api_key=expected['apiKey'],
            api_secret=expected['apiSecret']
        )
        assert actual == expected

        expected = {
            'type': 'SOAP_API',
            'baseURI': 'www.example.com',
            'authType': 'NONE'
        }
        actual = Instances.mkBaseNotifier(
            expected['type'], expected['baseURI'],
            auth_type=expected['authType']
        )
        assert actual == expected

        expected = {
            'type': 'REST_API',
            'baseURI': 'www.example.com/whatevs',
            'authType': 'BASIC',
            'grantType': 'PASSWORD',
            'userName': 'elvis',
            'password': 'graceland'
        }
        actual = Instances.mkBaseNotifier(
            expected['type'], expected['baseURI'],
            auth_type=expected['authType'],
            grant_type=expected['grantType'],
            user_name=expected['userName'],
            password=expected['password']
        )
        assert actual == expected

    def test_redaction(self):
        original = {
            'inboundConfig': {
                'authentication': {
                    'token': 'shakespeare'
                }
            },
            'outboundConfig': {
                'authentication': {
                    'apiKeyPairs': [{
                        'char1': 'juliet',
                        'char2': 'goneril'
                    }]
                }
            }
        }
        # make a copy and check that it really is a copy.
        tvalues = copy.deepcopy(original)
        assert tvalues is not original
        assert tvalues == original
        # the redact function should modify the dict in place, not copy it.
        result = Instances.redact_response(tvalues)
        assert result is tvalues
        # check the redaction did what we expected.
        original['inboundConfig']['authentication'][
            'token'] = 'REDACTED'
        original['outboundConfig']['authentication'][
            'apiKeyPairs'][0]['char1'] = 'REDACTED'
        original['outboundConfig']['authentication'][
            'apiKeyPairs'][0]['char2'] = 'REDACTED'
        assert result is not original
        assert result == original
