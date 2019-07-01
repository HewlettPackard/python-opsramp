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
import base64

from opsramp.base import ApiWrapper


class Rba(ApiWrapper):
    def __init__(self, parent):
        super(Rba, self).__init__(parent.api, 'rba')

    def category(self, uuid):
        return Category(self, uuid)

    def get_categories(self):
        return self.api.get('/categories')

    def create_category(self, name, parent_uuid=None):
        jjj = {'name': name}
        if parent_uuid:
            jjj['parent'] = parent_uuid
        return self.api.post('/categories', json=jjj)


class Category(ApiWrapper):
    def __init__(self, parent, uuid):
        super(Category, self).__init__(parent.api, 'categories/%s' % uuid)

    def script(self, uuid):
        return Script(self, uuid)

    def get_scripts(self):
        return self.api.get('/scripts')

    def create_script(self, script_definition):
        return self.api.post('/scripts', json=script_definition)


class Script(ApiWrapper):
    def __init__(self, parent, uuid):
        super(Script, self).__init__(parent.api, 'scripts/%s' % uuid)

    # Returns a string containing a base64 encoded version of the
    # content of the specified file. It was quite finicky to come
    # up with a method that works on both Python 2 and 3 so please
    # don't modify this, or test carefully if you do.
    @staticmethod
    def encode_payload(fname):
        with open(fname, 'rb') as f:
            content = base64.b64encode(f.read())
        return content.decode()

    # A helper function for use with mkparameter & mkscript.
    @staticmethod
    def mkattachment(name, payload):
        assert name
        return {
            'name': name,
            'file': payload
        }

    # Returns a Python dict that defines one parameter of a script.
    @staticmethod
    def mkparameter(name, description, datatype,
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
    def mkscript(name, description, platforms, execution_type, payload,
                 parameters=[],
                 script_name=None,
                 install_timeout=0,
                 registry_path=None,
                 registry_value=None,
                 process_name=None,
                 service_name=None,
                 output_directory=None,
                 output_file=None):
        if execution_type not in ('DOWNLOAD', 'EXE', 'MSI'):
            assert not output_directory
            assert not output_file
        if execution_type == 'COMMAND':
            payload_key = 'command'
            payload_value = payload
        else:
            payload_key = 'attachment'
            payload_value = Script.mkattachment(script_name, payload)

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
