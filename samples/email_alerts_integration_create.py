#!/usr/bin/env python
#
# Exercise the opsramp module as an illustration of how to use it.
#
# (c) Copyright 2019-2021 Hewlett Packard Enterprise Development LP
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
import yaml
import logging
import argparse

import opsramp.binding


def connect():
    url = os.environ['OPSRAMP_URL']
    key = os.environ['OPSRAMP_KEY']
    secret = os.environ['OPSRAMP_SECRET']
    return opsramp.binding.connect(url, key, secret)


def parse_argv():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        action='store_true'
    )
    ns = parser.parse_args()
    return ns


def main():
    ns = parse_argv()
    if ns.debug:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

    tenant_id = os.environ['OPSRAMP_TENANT_ID']

    ormp = connect()
    tenant = ormp.tenant(tenant_id)
    group = tenant.integrations().instances()

    # Create new Email Alerts Integration...
    jdata = {
        'displayName': 'Test Email Alerts integration',
        'emailProps': [{
            'name': 'logz.io email alert',
            'identifier': '^\\[Alert\\]',
            'identifierSource': 'EMAIL_SUBJECT',
            'properties': [{
                'name': 'Alert State',
                'defaultValue': 'OK',
                'condition': {
                    'contentSource': 'EMAIL_SUBJECT',
                    'operator': 'BETWEEN',
                    'startValue': '\\(',
                    'endValue': ' severity\\)'
                },
                'propertyMappings': {
                    'attrValues': [{
                        'attrValue': 'Critical',
                        'thirdPartyAttrValue': 'Severe'
                    },
                        {
                        'attrValue': 'Warning',
                        'thirdPartyAttrValue': 'High'
                    },
                        {
                        'attrValue': 'Observed',
                        'thirdPartyAttrValue': 'Medium'
                    },
                        {
                        'attrValue': 'Info',
                        'thirdPartyAttrValue': 'Low'
                    },
                        {
                        'attrValue': 'Ok',
                        'thirdPartyAttrValue': 'Info'
                    }]
                }
            },
                {
                'name': 'Service Name',
                'defaultValue': 'whatever',
                'condition': {
                    'contentSource': 'DEFAULT_VALUE'
                }
            },
                {
                'name': 'Device Host Name',
                'defaultValue': 'whatever',
                'condition': {
                    'contentSource': 'DEFAULT_VALUE'
                }
            }]
        }]
    }

    print('create integration using this payload')
    print(yaml.dump(jdata, default_flow_style=False))

    resp = group.create('Email Alerts', jdata)
    print('result:')
    print(yaml.dump(resp, default_flow_style=False))


if __name__ == "__main__":
    main()
