#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# metrics.py
# The OpsRamp metrics API is spread all over the place. This is a simple
# initial class to expose the "get metric time series values" API.
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

from opsramp.api import ORapi


class MetricsApi(ORapi):
    """The OpsRamp metrics API is spread all over the place. This is a simple
    initial class to expose the complete /metric (note no "s") tree."""

    def __init__(self, parent):
        super(MetricsApi, self).__init__(parent.api, "metric")
