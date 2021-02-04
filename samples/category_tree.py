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
    tid_list = [(tenant_id, '')]
    if not tenant.is_client():
        children = tenant.clients().get()
        cdata = [(x['uniqueId'], x['name']) for x in children]
        tid_list.extend(cdata)

    for uuid, name in tid_list:
        child = ormp.tenant(uuid)
        categs = child.rba().categories()
        clist = categs.get()
        print('{0} "{1}"'.format(uuid, name))
        for cdata in clist:
            show_contents(categs, cdata, 1)


def show_contents(categs, cdata, indent):
    print('{0} category {1:05d} {2}'.format(
        '..' * indent,
        cdata['id'],
        cdata['name']
    ))
    # get the list of scripts in the category.
    thiscat = categs.category(cdata['id'])
    try:
        scripts = thiscat.get()
    except RuntimeError as e:
        # we have encountered broken trees in the field so guard against it.
        print(e)
        scripts = []
    # print out a short description of each script.
    for s in scripts:
        print('{0}. script {1:06d} {2} {3} "{4}" "{5}"'.format(
            '..' * indent,
            s['id'],
            s['platforms'],
            s['executionType'],
            s['name'],
            s['description']
        ))
    # recurse into any embedded categories.
    if 'childs' in cdata:
        for child in cdata['childs']:
            show_contents(categs, child, indent + 1)


if __name__ == "__main__":
    main()
