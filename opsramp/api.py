#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# api.py
# OpsRamp-specific variant of ApiWrapper base class as a container for
# some methods and helpers that are common to multiple parts of that API.
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
import base64

from opsramp.base import ApiWrapper


class ORapi(ApiWrapper):
    '''OpsRamp-specific variant of ApiWrapper base class as a container for
    some methods and helpers that are common to multiple parts of that API.'''

    # Returns a string containing a base64 encoded version of the
    # content of the specified file. It was quite finicky to come
    # up with a method that works on both Python 2 and 3 so please
    # don't modify this, or test carefully if you do.
    @staticmethod
    def b64encode_payload(fname):
        with open(fname, 'rb') as f:
            content = base64.b64encode(f.read())
        return content.decode()

    def get(self, suffix='', headers=None):
        return self.api.get(suffix, headers)
