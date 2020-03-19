#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# metric.py
# Classes related to metrics
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
import datetime
from opsramp.base import ApiWrapper


class Metric(ApiWrapper):
    def __init__(self, parent, uuid):
        super(Metric, self).__init__(parent.api, 'metric')
        self.uuid = uuid

    def get(self, rtype, resource):
        suffix = '/tenants/%s/rtypes/%s/resources/%s/metrics' % \
                 (self.uuid, rtype, resource)
        return self.api.get(suffix)

    def search(self, rtype, resource, metric, starttime, endtime, ts_type):
        suffix='/search?tenant=%s&rtype=%s&' \
               'resource=%s&metric=%s&startTime=%s&endTime=%s' \
               '&timeseries_type=%s' % \
               (self.uuid, rtype, resource, metric, starttime, endtime, ts_type)
        return self.api.get(suffix)
