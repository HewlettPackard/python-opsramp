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

import os
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
    parser.add_argument(
        'uuid',
        type=str
    )
    ns = parser.parse_args()
    return ns


def create_command_script(targetcat):
    # Create a new RBA script in this category, with one parameter.
    # OpsRamp will prompt for a value for this parameter each time
    # you run this script in the UI and will pass the value in as $1
    # which you can see being used in the "payload" below.
    p1 = targetcat.mkParameter(
        name='venue',
        description='Where am I today?',
        datatype='STRING'
    )
    s1 = targetcat.mkScript(
        name='Hello <venue>',
        description='Stereotypical rock star intro',
        platforms=['LINUX'],
        execution_type='COMMAND',
        payload='echo "hello $1"',
        parameters=[p1]
    )
    print('creating new COMMAND script...')
    print(s1)
    resp = targetcat.create(s1)
    return resp


def create_python_script(targetcat):
    scriptfile = '/tmp/whatever-%s.py' % os.getpid()
    with open(scriptfile, 'w') as f:
        f.write('''#! /usr/bin/env python
from __future__ import print_function
print('hello world')
''')
    s1 = targetcat.mkScript(
        name='Python hello',
        description='Hello from Python land',
        platforms=['LINUX'],
        execution_type='PYTHON',
        script_name=os.path.basename(scriptfile),
        payload_file=scriptfile
    )
    print('creating new PYTHON script...')
    print(s1)
    resp = targetcat.create(s1)
    os.remove(scriptfile)
    return resp


def main():
    ns = parse_argv()
    if ns.debug:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
    category_id = int(ns.uuid)

    tenant_id = os.environ['OPSRAMP_TENANT_ID']

    ormp = connect()
    tenant = ormp.tenant(tenant_id)
    targetcat = tenant.rba().categories().category(category_id)

    # A "COMMAND" script is a basic oneliner that doesn't require a shell.
    resp = create_command_script(targetcat)
    print(resp)

    resp = create_python_script(targetcat)
    print(resp)


if __name__ == "__main__":
    main()
