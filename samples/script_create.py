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
import sys

import opsramp.binding
from opsramp.rba import Category


def connect():
    url = os.environ['OPSRAMP_URL']
    key = os.environ['OPSRAMP_KEY']
    secret = os.environ['OPSRAMP_SECRET']
    return opsramp.binding.connect(url, key, secret)


def main():
    tenant_id = os.environ['OPSRAMP_TENANT_ID']

    if len(sys.argv) != 2:
        print('usage: %s <category id>' % sys.argv[0])
        exit(2)
    category_id = int(sys.argv[1])

    ormp = connect()
    tenant = ormp.tenant(tenant_id)
    targetcat = tenant.rba().categories().category(category_id)

    # Create a new RBA script in this category, with one parameter.
    # OpsRamp will prompt for a value for this parameter each time
    # you run this script in the UI and will pass the value in as $1
    # which you can see being used in the "payload" below.
    p1 = Category.mkparameter(
        name='venue',
        description='Where am I today?',
        datatype='STRING'
    )
    s1 = Category.mkscript(
        name='Hello <venue>',
        description='Stereotypical rock star intro',
        platforms=['LINUX'],
        execution_type='COMMAND',
        payload='echo "hello $1"',
        parameters=[p1]
    )
    print('creating new COMMAND script in category', category_id, '...')
    resp = targetcat.create(s1)
    print(resp)


if __name__ == "__main__":
    main()
