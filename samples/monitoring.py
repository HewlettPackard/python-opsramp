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

# From Opsramp API Documentation e.g.
# https://docs.opsramp.com/monitoring-apis/
# https://docs.opsramp.com/metric-apis/
#
# Assign Templates to Resource
# Search Templates
# Get Assigned Templates of Resource
# Unassign Templates from Resource
#
# Save Metrics on a Resource
# Get Metrics on a Resource
# Get Metric Type
# Get Metric (Time series) on a Resource
#
# https://<api-url>/api/v2/metric/tenants/{clientId}/rtypes/{rtype}/resources/{resource}/metrics
# https://<api-url>/api/v2/metric/search?tenant=client_20&rtype=DEVICE&resource=ab342123-5bfb-434c-aae4-03611ca020d9&metric=system.cpu.utilization&startTime=1536643494&endTime=1536661494
# https://sramp.com/api/v2//tenants/client_2703/resources/search
# https://<api-url>/api/v2/tenants/{tenantId}/resources/search
from __future__ import print_function
import os
import yaml
import json
import time

import opsramp.binding
import opsramp.metric
import opsramp.resources


def connect():
    url = os.environ['OPSRAMP_URL']
    key = os.environ['OPSRAMP_KEY']
    secret = os.environ['OPSRAMP_SECRET']
    return opsramp.binding.connect(url, key, secret)

def main():
    tenant_id = os.environ['OPSRAMP_TENANT_ID']
    device_id = os.environ['OPSRAMP_DEVICE_ID']

    ormp = connect()
    tenant = ormp.tenant(tenant_id)
    monitoring = tenant.monitoring()
    templates = monitoring.templates()

    # Get list of Opsramp Resources for this tenant
    resources = ormp.resources(tenant_id)
    res = resources.search()
    pretty_res = json.dumps(res, sort_keys=True, indent=4, separators=('.', ': '))
    print("resources: %s\n" % pretty_res)

    # Get a list of Opsramp Templates for this tenant
    res = templates.search()
    pretty_res = json.dumps(res, sort_keys=True, indent=4, separators=('.', ': '))
    print("Templates Search: %s\n" % pretty_res)

    # An example of getting Opsramp Metrics of type 'DEVICE' for a particular
    # Resource within a particular tenant.
    rtype = 'DEVICE'
    metrics = ormp.metric(tenant_id)
    res = metrics.get(rtype, device_id)
    pretty_res = json.dumps(res, sort_keys=True, indent=4, separators=('.', ': '))
    print("Metrics: %s\n" % pretty_res)

    # An example of getting time-based Opsramp metrics for
    # a particular resource within a particular tenant.
    rtype = 'DEVICE'
    metrics = ormp.metric(tenant_id)
    metric_name = "azure.cpu"
    starttime = int((time.time() - (60*60*24)))
    endtime = int(time.time())
    ts_type = "RealTime"

    res = metrics.search(rtype, device_id, metric_name, starttime, endtime, ts_type)
    pretty_res = json.dumps(res, sort_keys=True, indent=4, separators=('.', ': '))
    print("Time Series Metrics: %s\n" % pretty_res)

if __name__ == "__main__":
    main()
