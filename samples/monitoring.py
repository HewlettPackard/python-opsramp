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
# https://sramp.com/api/v2//tenants/client_2703/resources/search
# https://<api-url>/api/v2/tenants/{tenantId}/resources/search
from __future__ import print_function
import os
import yaml

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

    ormp = connect()
    tenant = ormp.tenant(tenant_id)
    monitoring = tenant.monitoring()
    templates = monitoring.templates()

    resources = ormp.resources(tenant_id)
    res = resources.search()
    # print("resources: %s\n" % res)

    # res = templates.search()
    # print("Templates Search: %s\n" % res)

    rtype = 'DEVICE'
    resource = '9e8b99ad-f9db-4e81-bfad-40249d9d9dac'
    # metrics = ormp.metric.get(tenant_id, rtype, resource)
    metrics = ormp.metric(tenant_id)
    res = metrics.get(rtype, resource)
    print("Metrics: %s\n" % res)
if __name__ == "__main__":
    main()
