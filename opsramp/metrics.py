#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# metrics.py
# Classes dealing directly with OpsRamp Metrics.
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
from opsramp.base import ApiWrapper


class Metrics(ApiWrapper):
    def __init__(self, parent):
        text_to_remove = '/tenants'
        stripped_url = parent.api.baseurl.split(text_to_remove, 1)[0]
        parent.api.baseurl = stripped_url + '/metric'
        super(Metrics, self).__init__(parent.api, '')

    def getMetricsValues(self, query_string=''):
        suffix = '/search'
        if query_string:
            suffix += '?' + query_string
        return self.api.get(suffix)
