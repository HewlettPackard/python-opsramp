#!/usr/bin/env python
#
# Exercise the opsramp module as an illustration of how to use it.
#
# (c) Copyright 2020 Hewlett Packard Enterprise Development LP
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

tnt_id = os.environ['OPSRAMP_TENANT_ID']


def connect():
    url = os.environ['OPSRAMP_URL']
    key = os.environ['OPSRAMP_KEY']
    secret = os.environ['OPSRAMP_SECRET']
    return opsramp.binding.connect(url, key, secret)


def walk(map):
    if map['childType'] != 'SERVICE':
        # print("LEAF! %s %s" % (map['id'], map['name']))
        print("LEAF! %s" % map)
    else:
        # print("BRANCH! %s %s" % (map['id'], map['name']))
        print("BRANCH! %s" % map)
        maps = service_maps.get(map['id'])
        if 'results' in maps:
            for submap in maps['results']:
                walk(submap)


ormp = connect()
tnt = ormp.tenant(tnt_id)
service_maps = tnt.service_maps()


def main():
    resp = service_maps.get()
    for map in resp['results']:
        walk(map)


if __name__ == "__main__":
    main()
