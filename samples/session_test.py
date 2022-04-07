#!/usr/bin/env python
#
# (c) Copyright 2020-2022 Hewlett Packard Enterprise Development LP
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
import requests


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
