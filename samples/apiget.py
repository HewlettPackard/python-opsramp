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
import yaml
import sys
import logging

import opsramp.binding


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    endpoint = os.environ['OPSRAMP_URL']
    key = os.environ['OPSRAMP_KEY']
    secret = os.environ['OPSRAMP_SECRET']

    suffix = sys.argv[1]
    ormp = opsramp.binding.connect(endpoint, key, secret)
    resp = ormp.get(suffix)
    print(yaml.dump(resp, default_flow_style=False))


if __name__ == "__main__":
    main()
