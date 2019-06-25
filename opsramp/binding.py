#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
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
import requests
import base64


def connect(url, key, secret):
    auth_url = url + '/auth/oauth/token'
    auth_hdrs = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json,application/xml'
    }
    body = 'grant_type=client_credentials&' \
           'client_id=%s&' \
           'client_secret=%s' % (key, secret)
    ao = ApiObject(auth_url, auth_hdrs)
    auth_resp = ao.post(data=body)
    token = auth_resp['access_token']
    return Opsramp(url, token)


class PathTracker(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.prefix = ''
        self.stack = []

    def __str__(self):
        return '%s "%s" %s' % (str(type(self)), self.prefix, self.stack)

    def clone(self):
        new1 = PathTracker()
        new1.prefix = self.prefix
        new1.stack = self.stack
        return new1

    def cd(self, path):
        # no support for '..' right now, maybe in the future
        if path[0] == '/':
            self.prefix = path
        else:
            self.prefix += '/' + path
        self.prefix = self.prefix.strip('/')
        return self.prefix

    def pushd(self, path):
        self.stack.append(self.prefix)
        return self.cd(path)

    def popd(self):
        self.prefix = self.stack.pop()
        return self.prefix

    def fullpath(self, suffix=''):
        if len(suffix) > 0 and suffix[0] == '/':
            retval = suffix
        else:
            retval = ''
            if len(self.prefix) > 0:
                retval += '/' + self.prefix
            if len(suffix) > 0:
                retval += '/' + suffix
        return retval


class ApiObject(object):
    def __init__(self, url, auth, tracker=None):
        self.baseurl = url.rstrip('/')
        self.auth = auth
        if tracker:
            self.tracker = tracker
        else:
            self.tracker = PathTracker()

    def __str__(self):
        return '%s "%s" "%s"' % (
            str(type(self)), self.baseurl, self.tracker.fullpath()
        )

    def clone(self):
        new1 = ApiObject(self.baseurl, self.auth, self.tracker.clone())
        return new1

    def cd(self, path):
        return self.tracker.cd(path)

    def pushd(self, path):
        return self.tracker.pushd(path)

    def popd(self):
        return self.tracker.popd()

    def chroot(self, suffix=''):
        suffix = self.tracker.fullpath(suffix)
        if suffix:
            self.baseurl += suffix
            self.tracker.reset()
        return ''

    def compute_url(self, suffix=''):
        retval = self.baseurl
        suffix = self.tracker.fullpath(suffix)
        if suffix:
            retval += suffix
        return retval.rstrip('/')

    def prep_headers(self, headers):
        if not headers:
            return self.auth
        hdr = {}
        hdr.update(self.auth)
        hdr.update(headers)
        return hdr

    @staticmethod
    def process_result(url, resp):
        if resp.status_code != requests.codes.OK:
            msg = '%s %s %s' % (resp, url, resp.content)
            raise RuntimeError(msg)
        try:
            return resp.json()
        except: # noqa
            return resp.text

    def get(self, suffix='', headers={}):
        url = self.compute_url(suffix)
        hdr = self.prep_headers(headers)
        resp = requests.get(url, headers=hdr)
        return self.process_result(url, resp)

    def post(self, suffix='', headers={}, data=None, json=None):
        url = self.compute_url(suffix)
        hdr = self.prep_headers(headers)
        resp = requests.post(url, headers=hdr, data=data, json=json)
        return self.process_result(url, resp)


class ApiWrapper(object):
    def __init__(self, apiobject, suffix=''):
        self.api = apiobject.clone()
        if suffix:
            self.api.chroot(suffix)

    def __str__(self):
        return '%s %s' % (str(type(self)), self.api)


class Opsramp(ApiWrapper):
    def __init__(self, url, token):
        self.auth = {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json,application/xml'
        }
        apiobject = ApiObject(url + '/api/v2', self.auth)
        super(Opsramp, self).__init__(apiobject)

    def __str__(self):
        return '%s %s' % (str(type(self)), self.api)

    def tenant(self, name):
        return Tenant(self, name)

    def get_alert_types(self):
        return self.api.get('/alertTypes')


class Tenant(ApiWrapper):
    def __init__(self, parent, uuid):
        super(Tenant, self).__init__(parent.api, 'tenants/%s' % uuid)

    def rba(self):
        return Rba(self)

    def monitoring(self):
        return Monitoring(self)

    def get_alerts(self, searchpattern):
        return self.api.get('/alerts/search?queryString=%s' % searchpattern)

    def get_agent_script(self):
        hdr = {'Accept': 'application/octet-stream,application/xml'}
        return self.api.get('agents/deployAgentsScript', headers=hdr)


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

    def get(self):
        return self.api.get()

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


class Monitoring(ApiWrapper):
    def __init__(self, parent):
        super(Monitoring, self).__init__(parent.api, 'monitoring')

    def templates(self):
        return Templates(self)


class Templates(ApiWrapper):
    def __init__(self, parent):
        super(Templates, self).__init__(parent.api, 'templates')

    def search(self, pattern=''):
        suffix = '/search'
        if pattern:
            suffix += '?' + pattern
        return self.api.get(suffix)
