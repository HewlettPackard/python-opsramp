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
import logging
import os

import opsramp.binding
import yaml


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

    ormp = connect()
    partner = ormp.tenant(partner_id)

    group = partner.mgmt_profiles()
    resp = group.search()
    print("%s management profiles" % resp["totalResults"])
    pretty_set = yaml.dump(resp["results"])
    print(pretty_set)

    # The links are weird in this part of OpsRamp. A search at partner level
    # returns a list of all profiles from all clients, but you can't get an
    # individual profile by ID from partner level. Instead you have to find
    # the ID of the *client* the profile is in, and then navigate down from
    # the top to that client object and use it to do the get().
    profile0 = resp["results"][0]
    clientid = profile0["client"]["uniqueId"]

    obj = ormp.tenant(clientid).mgmt_profiles().get(profile0["id"])
    print(yaml.dump(obj))


if __name__ == "__main__":
    main()
