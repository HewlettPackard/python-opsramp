#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# monitoring.py
# Classes related to monitoring templates and similar things.
#
# (c) Copyright 2019-2021 Hewlett Packard Enterprise Development LP
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


class Monitoring(ORapi):
    def __init__(self, parent):
        super(Monitoring, self).__init__(parent.api, 'monitoring')

    def templates(self):
        return Templates(self)


class Templates(ORapi):
    def __init__(self, parent):
        super(Templates, self).__init__(parent.api, 'templates')
