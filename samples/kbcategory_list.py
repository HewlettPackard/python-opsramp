#!/usr/bin/env python
#
# Exercise the opsramp module as an illustration of how to use it.
#
# (c) Copyright 2019-2025 Hewlett Packard Enterprise Development LP
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


def connect():
    url = os.environ["OPSRAMP_URL"]
    key = os.environ["OPSRAMP_KEY"]
    secret = os.environ["OPSRAMP_SECRET"]
    return opsramp.binding.connect(url, key, secret)


def parse_argv():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    ns = parser.parse_args()
    return ns


def main():
    ns = parse_argv()
    if ns.debug:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

    tenant_id = os.environ["OPSRAMP_TENANT_ID"]

    ormp = connect()
    tenant = ormp.tenant(tenant_id)

    kb = tenant.kb()
    categs = kb.categories()
    articles = kb.articles()

    allcats = categs.search()
    clist = allcats["results"]
    print(f"{len(clist)} categories")
    # for each category
    for cdata in clist:
        categ_id = cdata["id"]
        categ_name = cdata["name"]
        print("category", categ_id, f'"{categ_name}"')
        # for each article in this category
        alist = articles.search(f"categoryId={categ_id}")
        for s in alist["results"]:
            print(
                ". article",
                s["id"],
                s["subject"],
            )
            if ns.verbose:
                print(f'.. content "{s["content"]}"')


if __name__ == "__main__":
    main()
