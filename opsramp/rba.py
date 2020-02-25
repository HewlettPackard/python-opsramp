#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# rba.py
# Runbook Automation related classes
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

from opsramp.base import ApiWrapper, Helpers


class Rba(ApiWrapper):
    def __init__(self, parent):
        super(Rba, self).__init__(parent.api, 'rba')

    def categories(self):
        return Categories(self)


class Categories(ApiWrapper):
    def __init__(self, parent):
        super(Categories, self).__init__(parent.api, 'categories')

    # Creates a new category with optional parent.
    def create(self, name, parent_uuid=None):
        jjj = {'name': name}
        if parent_uuid:
            jjj['parent'] = {
                'id': parent_uuid
            }
        return self.api.post(json=jjj)

    def category(self, uuid):
        return Category(self, uuid)

    # Updates an RBA category based on its ID.
    def update(self, uuid, definition):
        # Making sure the UUID is specified in the request body as it's not
        # specified in the URL for some reason.
        definition['id'] = uuid
        return self.api.put('', json=definition)

    # Deletes an RBA category based on its ID
    def delete(self, uuid):
        return self.api.delete('%s' % uuid)


class Category(ApiWrapper):
    def __init__(self, parent, uuid):
        super(Category, self).__init__(parent.api, '%s/scripts' % uuid)

    # Creates a script in this category
    def create(self, definition):
        return self.api.post(json=definition)

    # Updates a script given the id
    def update(self, uuid, definition):
        return self.api.post('%s' % uuid, json=definition)

    # Deletes a script given by the id
    def delete(self, uuid):
        return self.api.delete('%s' % uuid)

    # A helper function for use with mkParameter & mkScript.
    @staticmethod
    def mkAttachment(name, payload):
        assert name
        assert payload
        return {
            'name': name,
            'file': payload
        }

    # Returns a Python dict that defines one parameter of a script.
    @staticmethod
    def mkParameter(name, description, datatype,
                    optional=False, default=None):
        assert name
        assert description
        assert datatype
        if optional:
            assert default is not None
        return {
            'name': name,
            'description': description,
            'dataType': datatype,
            'type': 'OPTIONAL' if optional else 'REQUIRED',
            'defaultValue': default
        }

    # Returns a Python dict that defines a new RBA script. Intended
    # for use with Category.create_script() it also asserts that
    # certain rules are being complied with in the script definition.
    @staticmethod
    def mkScript(name, description, platforms, execution_type,
                 payload=None,
                 payload_file=None,
                 parameters=[],
                 script_name=None,
                 install_timeout=0,
                 registry_path=None,
                 registry_value=None,
                 process_name=None,
                 service_name=None,
                 output_directory=None,
                 output_file=None):
        assert name
        assert description
        assert platforms
        assert execution_type
        if payload_file:
            assert not payload
            payload = Helpers.b64encode_payload(payload_file)
        assert payload
        if execution_type not in ('DOWNLOAD', 'EXE', 'MSI'):
            assert not output_directory
            assert not output_file
        if execution_type == 'COMMAND':
            payload_key = 'command'
            payload_value = payload
        else:
            assert script_name
            payload_key = 'attachment'
            payload_value = Category.mkAttachment(script_name, payload)

        # fields that are always present.
        retval = {
            'name': name,
            'description': description,
            'platforms': platforms,
            'executionType': execution_type,
            payload_key: payload_value
        }

        # optional ones.
        if parameters:
            retval['parameters'] = parameters

        if install_timeout:
            retval['installTimeout'] = install_timeout

        if 'WINDOWS' not in platforms:
            assert not registry_path
            assert not registry_value
        else:
            if registry_path:
                retval['registryPath'] = registry_path
                if registry_value:
                    retval['registryValue'] = registry_value

        if 'LINUX' not in platforms:
            assert not process_name
            assert not service_name
        else:
            if process_name:
                retval['processName'] = process_name
            if service_name:
                retval['serviceName'] = service_name

        return retval
