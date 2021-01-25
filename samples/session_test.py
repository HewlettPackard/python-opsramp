#!/usr/bin/env python
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

from __future__ import print_function
import os
import json
import requests
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
    if ns.debug:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
    return ns


def main():
    parse_argv()

    ormp = connect()

    # use a custom session with default parameters.
    my_session = requests.session()
    ormp.session = my_session

    # simple demo that the custom session works.
    assert ormp.session is my_session
    global_cfg = ormp.config()
    tzs = global_cfg.get_timezones()
    print('[')
    for t in tzs:
        print('  ', json.dumps(t))
    print(']')
    # check that the custom session is still in use.
    assert ormp.session is my_session


if __name__ == "__main__":
    main()
