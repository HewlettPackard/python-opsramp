#!/usr/bin/env python
#
# A command line interface to OpsRamp that illustrates how to use
# this language binding as well as being useful in its own right.
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
import os

import opsramp.binding


# TODO make these optional command line parameters
OPSRAMP_URL = os.environ["OPSRAMP_URL"]
OPSRAMP_KEY = os.environ["OPSRAMP_KEY"]
OPSRAMP_SECRET = os.environ["OPSRAMP_SECRET"]
OPSRAMP_TENANT_ID = os.environ["OPSRAMP_TENANT_ID"]


def do_auth():
    return opsramp.binding.connect(OPSRAMP_URL, OPSRAMP_KEY, OPSRAMP_SECRET)


# Ideas for the cli syntax:
#
# ormpcli \
#   --tenant=client_2703 \
#   --endpoint=https://hpe-dev.api.try.opsramp.com \
#   --key='redacted' \
#   --secret='redacted' \
#   subtree area action
#
# ormpcli tenant agent script
# ormpcli tenant rba categories
# ormpcli tenant monitoring templates


def parse_args():
    parser = argparse.ArgumentParser(description="HPE cli for OpsRamp")
    parser.add_argument("subtree")
    parser.add_argument("area")
    parser.add_argument("action")
    return parser.parse_args()


def do_tenant_rba_action(rba, action):
    if action == "categories":
        clist = rba.categories().get()
        print(json.dumps(clist))
    else:
        raise ValueError(rba, action)


def do_tenant_monitoring_action(monitoring, action):
    if action == "templates":
        tplates = monitoring.templates()
        resp = tplates.search()
        print(resp["totalResults"], "monitoring templates found")
    else:
        raise ValueError(monitoring, action)


def do_tenant_action(tenant, area, action):
    if area == "rba":
        subapi = tenant.rba()
        return do_tenant_rba_action(subapi, action)
    elif area == "monitoring":
        subapi = tenant.monitoring()
        return do_tenant_monitoring_action(subapi, action)
    elif area == "agent" and action == "script":
        contents = tenant.get_agent_script()
        print(contents)
    else:
        raise ValueError(tenant, area, action)


def do_action(ormp, subtree, area, action):
    if subtree == "tenant":
        tenant = ormp.tenant(OPSRAMP_TENANT_ID)
        return do_tenant_action(tenant, area, action)
    else:
        raise ValueError(subtree, area, action)


def main():
    args = parse_args()
    ormp = do_auth()
    do_action(ormp, args.subtree, args.area, args.action)


if __name__ == "__main__":
    main()
