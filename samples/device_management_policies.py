#!/usr/bin/env python
#
# Exercise the opsramp module as an illustration of how to use it.
#
# (c) Copyright 2019-2022 Hewlett Packard Enterprise Development LP
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

import argparse
import json
import logging
import os

import opsramp.binding


def connect():
    url = os.environ["OPSRAMP_URL"]
    key = os.environ["OPSRAMP_KEY"]
    secret = os.environ["OPSRAMP_SECRET"]
    return opsramp.binding.connect(url, key, secret)


def parse_argv():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    ns = parser.parse_args()
    return ns


def main():
    ns = parse_argv()
    if ns.debug:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

    partner_id = os.environ["OPSRAMP_TENANT_ID"]
    dmp_name = os.environ["OPSRAMP_DMP_NAME"]

    ormp = connect()
    partner = ormp.tenant(partner_id)

    policies = partner.policies()
    dmps = policies.get()
    pretty_dmps = json.dumps(dmps, sort_keys=True)
    print("All DMPs: %s\n" % pretty_dmps)

    my_dmp = policies.search(dmp_name)
    pretty_dmps = json.dumps(my_dmp, sort_keys=True)
    print("Specific DMP: %s:\n%s" % (dmp_name, pretty_dmps))


if __name__ == "__main__":
    main()
