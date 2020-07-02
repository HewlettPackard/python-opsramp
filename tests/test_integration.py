#!/usr/bin/env python
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
import base64
import copy
import unittest
import requests_mock

import opsramp.binding
from opsramp.integrations import Instances


class InstancesTest(unittest.TestCase):
    def setUp(self):
        fake_url = 'http://api.example.com'
        fake_token = 'unit-test-fake-token'
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        self.fake_client_id = 'client_for_unit_test'
        self.client = self.ormp.tenant(self.fake_client_id)
        assert self.client.is_client()

        self.integs = self.client.integrations()
        assert 'Integrations' in str(self.integs)

    def test_itypes(self):
        group = self.integs.itypes()
        pattern = 'whatever'
        url = group.api.compute_url('search?%s' % pattern)
        expected = ['unit', 'test', 'list']
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected)
            actual = group.search(pattern)
        assert actual == expected
        # check the compatibility function would return the
        # same type of object, so there's no need to repeat
        # all of the tests for it.
        assert isinstance(self.integs.available(), type(group))

    def test_instances(self):
        group = self.integs.instances()
        pattern = 'whatever'
        url = group.api.compute_url('search?%s' % pattern)
        expected = ['unit', 'test', 'list']
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected)
            actual = group.search(pattern)
        assert actual == expected
        # check the compatibility function would return the
        # same type of object, so there's no need to repeat
        # all of the tests for it.
        assert isinstance(self.integs.installed(), type(group))

    def test_instance_kubernetes_configuration(self):
        group = self.integs.instances()
        thisid = 123456
        url = group.api.compute_url('%s/configFile/kubernetes' % thisid)
        expected = [{'unit': 'test'}]
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected)
            actual = group.get_kubernetes_configuration(uuid=thisid)
        assert actual == expected

    def test_instance_create(self):
        group = self.integs.instances()
        name = 'unit-test-integration'
        url = group.creator_api.compute_url(name)
        expected = {'unit': 'test'}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.create(type_name=name, definition=expected)
        assert actual == expected

    def test_instance_update(self):
        group = self.integs.instances()
        newid = 123456
        url = group.api.compute_url(newid)
        expected = {'unit': 'test'}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.update(uuid=newid, definition=expected)
        assert actual == expected

    def test_instance_enable(self):
        group = self.integs.instances()
        thisid = 789012
        url = group.api.compute_url('%s/enable' % thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.enable(uuid=thisid)
        assert actual == expected

    def test_instance_disable(self):
        group = self.integs.instances()
        thisid = 345678
        url = group.api.compute_url('%s/disable' % thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.disable(uuid=thisid)
        assert actual == expected

    def test_instance_delete(self):
        group = self.integs.instances()
        thisid = 999999
        url = group.api.compute_url('%s' % thisid)

        expected_response = {'id': thisid}

        # Test that a delete works as expected if reason not provided
        expected_send = {"uninstallReason": "<Not specified>"}
        with requests_mock.Mocker() as m:
            adapter = m.delete(url, json=expected_response)
            actual_response = group.delete(uuid=thisid)
            assert adapter.last_request.json() == expected_send
            assert actual_response == expected_response

        # Test that a delete works as expected if we provide a reason
        delete_reason = 'Totally fake reason to delete something'
        expected_send = {"uninstallReason": delete_reason}
        with requests_mock.Mocker() as m:
            adapter = m.delete(url, json=expected_response)
            actual_response = group.delete(
                uuid=thisid,
                uninstall_reason=delete_reason
            )
            assert adapter.last_request.json() == expected_send
            assert actual_response == expected_response

    def test_instance_notifier(self):
        group = self.integs.instances()
        thisid = 901234
        url = group.api.compute_url('%s/notifier' % thisid)
        expected = {'id': thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected)
            actual = group.notifier(uuid=thisid, definition=expected)
        assert actual == expected

    def test_instance_auth_type(self):
        group = self.integs.instances()
        thisid = 567890
        url = group.api.compute_url('%s/inbound/authentication' % thisid)
        with requests_mock.Mocker() as m:
            for key in 'OAUTH2', 'WEBHOOK', 'BASIC':
                expected = {'type': key}
                m.post(url, json=expected)
                actual = group.set_auth_type(uuid=thisid, auth_type=key)
                assert actual == expected
            with self.assertRaises(AssertionError):
                group.set_auth_type(uuid=thisid, auth_type='unit test value')

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

    def test_valuemap(self):
        expected = [
            {
                'attrValue': 'client_113',
                'tenantAttrValue': '22cdbc5bb401d737b088c9'
            },
            {
                'attrValue': 'client_843',
                'tenantAttrValue': '66cdbc5bb401d737b088c9'
            }
        ]
        actual = Instances.mkValueMap(
            ('attrValue', 'tenantAttrValue'),
            (('client_113', '22cdbc5bb401d737b088c9'),
             ('client_843', '66cdbc5bb401d737b088c9'))
        )
        assert actual == expected

        expected = [
            {
                'attrValue': 'Fido',
                'thirdPartyAttrValue': 'His Royal Fidoness'
            },
            {
                'attrValue': 'brown',
                'thirdPartyAttrValue': 'Autumn Sunset'
            }
        ]
        actual = Instances.mkValueMap(
            ('attrValue', 'thirdPartyAttrValue'),
            (('Fido', 'His Royal Fidoness'),
             ('brown', 'Autumn Sunset'))
        )
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
