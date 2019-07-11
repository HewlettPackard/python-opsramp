#!/usr/bin/env python
#
# Exercise the opsramp module as an illustration of how to use it.
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

import opsramp.binding

subscription = os.environ['AZURE_SUBSCRIPTION']
azure_tenant = os.environ['AZURE_TENANT_ID']
azure_client = os.environ['AZURE_CLIENT_ID']
azure_secret = os.environ['AZURE_SECRET_KEY']


def connect():
    url = os.environ['OPSRAMP_URL']
    key = os.environ['OPSRAMP_KEY']
    secret = os.environ['OPSRAMP_SECRET']
    return opsramp.binding.connect(url, key, secret)


def main():
    tenant_id = os.environ['OPSRAMP_TENANT_ID']

    ormp = connect()
    tnt = ormp.tenant(tenant_id)

    # Create new discovery profile...
    jdata = [{
        'name': 'whatever',
        'credential': {
            'credentialType': 'Azure',
            'AzureType': 'ARM',
            'SubscriptionId': subscription,
            'TenantId': azure_tenant,
            'ClientID': azure_client,
            'SecretKey': azure_secret
        },
        'policy': {
            'name': 'whatever',
            'resourceType': 'ALL',
            'entityType': 'ALL',
            'rules': [{
                'filterType': 'ANY_DEVICE'
            }],
            'actions': [{
                'action': 'MANAGE DEVICE',
                'items': [],
                'forceAssignOrUnassign': False
            }],
            'matchType': 'ANY'
        },
        'schedule': {
            'patternType': 'MINUTES',
            'pattern': '30',
            'startTime': '00:30:00'
        }
    }]

    resp = tnt.discovery().create(jdata)
    print(resp)


if __name__ == "__main__":
    main()
