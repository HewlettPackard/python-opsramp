#!/usr/bin/env python
#
# Exercise the opsramp module as an illustration of how to use it.
#
# (c) Copyright 2020-2021 Hewlett Packard Enterprise Development LP
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

tnt_id = os.environ['OPSRAMP_TENANT_ID']


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

    ormp = connect()
    tnt = ormp.tenant(tnt_id)
    service_maps = tnt.service_maps()

    top_level_json = [{
        "name": "Finance Inventory",
        "createdDate": "2018-06-20T11:33:08+0000",
        "updatedDate": "2018-06-20T11:33:08+0000",
        "childType": "SERVICE",
        "frequency": 5,
        "thresholdType": "count",
        "thresholdLimit": 1,
        "monitorNames": ["service.availability.metric"],
        "include": "ALL",
        "type": "alert",
        "alertType": 2,
        "alert": False,
        "metrics": []
    }]

    resp = service_maps.create(top_level_json)

    top_level_sgid = resp[0]['id']

    # Now create two sub-maps attached to the top level one above.

    second_level_json_dept_a = [{
        "name": "Department A",
        "createdDate": "2018-06-20T11:33:08+0000",
        "updatedDate": "2018-06-20T11:33:08+0000",
        "childType": "SERVICE",
        "frequency": 5,
        "thresholdType": "count",
        "thresholdLimit": 1,
        "monitorNames": ["service.availability.metric"],
        "include": "ALL",
        "type": "alert",
        "alertType": 2,
        "alert": False,
        "metrics": [],
        "parent": {
                "id": top_level_sgid
        }
    }]

    second_level_json_dept_b = [{
        "name": "Department B",
        "createdDate": "2018-06-20T11:33:08+0000",
        "updatedDate": "2018-06-20T11:33:08+0000",
        "childType": "SERVICE",
        "frequency": 5,
        "thresholdType": "count",
        "thresholdLimit": 1,
        "monitorNames": ["service.availability.metric"],
        "include": "ALL",
        "type": "alert",
        "alertType": 2,
        "alert": False,
        "metrics": [],
        "parent": {
            "id": top_level_sgid
        }
    }]

    resp = service_maps.create(second_level_json_dept_a)
    second_level_sgid_dept_a = resp[0]['id']

    resp = service_maps.create(second_level_json_dept_b)
    second_level_sgid_dept_b = resp[0]['id']

    print("dept a %s dept b %s" %
          (second_level_sgid_dept_a, second_level_sgid_dept_b))

    vm_map_json = [{
        "name": "Warehouse Inventory",
        "createdDate": "2018-06-20T11:33:08+0000",
        "updatedDate": "2018-06-20T11:33:08+0000",
        "childType": "DEVICE",
        "frequency": 5,
        "thresholdType": "count",
        "thresholdLimit": 1,
        "monitorNames": [
            "service.availability.metric"
        ],
        "include": "ALL",
        "type": "alert",
        "alertType": 2,
        "alert": False,
        "metrics": [],
        "filterCriteria": {
            "matchType": "ANY",
            "rules": [{
                "key": "Device Name",
                "operator": "Contains",
                "value": "Linux",
                "resourceType": "DEVICE"
            }]
        },
        "parent": {
            "id": second_level_sgid_dept_b
        }
    }]

    resp = service_maps.create(vm_map_json)
    vm_map_sgid = resp[0]['id']

    print("vm map sgid %s" % vm_map_sgid)


if __name__ == "__main__":
    main()
