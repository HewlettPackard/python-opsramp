#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# msp.py
# Classes related to partner-level actions.
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
from opsramp.base import ApiWrapper


class Clients(ApiWrapper):
    def __init__(self, parent):
        super(Clients, self).__init__(parent.api, 'clients')

    def get_list(self):
        return self.api.get('/minimal')

    def client(self, uuid):
        return Client(self, uuid)

    def create_client(self, client_definition):
        return self.api.post('', json=client_definition)


class Client(ApiWrapper):
    def __init__(self, parent, uuid):
        assert uuid[:7] == 'client_'
        super(Client, self).__init__(parent.api, '%s' % uuid)

    def get(self):
        return self.api.get()
