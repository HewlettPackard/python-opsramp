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
import json

import opsramp.binding


def connect():
    url = os.environ['OPSRAMP_URL']
    key = os.environ['OPSRAMP_KEY']
    secret = os.environ['OPSRAMP_SECRET']
    return opsramp.binding.connect(url, key, secret)


def main():
    tnt_id = os.environ['OPSRAMP_TENANT_ID']

    assert len(sys.argv) == 2
    uniqueId = sys.argv[1]

    ormp = connect()
    tnt = ormp.tenant(tnt_id)

    group = tnt.sites()
    resp = group.get(uniqueId)
    print(json.dumps(resp, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
