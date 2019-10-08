#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# base.py
# Containing various base classes used in other parts of the library
# but not intended for direct use by callers.
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
import requests


class Helpers(object):
    # Returns a string containing a base64 encoded version of the
    # content of the specified file. It was quite finicky to come
    # up with a method that works on both Python 2 and 3 so please
    # don't modify this, or test carefully if you do.
    @staticmethod
    def b64encode_payload(fname):
        with open(fname, 'rb') as f:
            content = base64.b64encode(f.read())
        return content.decode()


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
        suffix = str(suffix)
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
        self.tracker.cd(path)
        return self.compute_url()

    def pushd(self, path):
        self.tracker.pushd(path)
        return self.compute_url()

    def popd(self):
        self.tracker.popd()
        return self.compute_url()

    def chroot(self, suffix=''):
        suffix = self.tracker.fullpath(suffix)
        if suffix:
            self.baseurl += suffix
            self.tracker.reset()
        return self.compute_url()

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
            msg = '%s %s %s %s' % (
                resp,
                resp.request.method,
                url,
                resp.content
            )
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

    def put(self, suffix='', headers={}, data=None, json=None):
        url = self.compute_url(suffix)
        hdr = self.prep_headers(headers)
        resp = requests.put(url, headers=hdr, data=data, json=json)
        return self.process_result(url, resp)

    def delete(self, suffix='', headers={}):
        url = self.compute_url(suffix)
        hdr = self.prep_headers(headers)
        resp = requests.delete(url, headers=hdr)
        return self.process_result(url, resp)


class ApiWrapper(object):
    def __init__(self, apiobject, suffix=''):
        self.api = apiobject.clone()
        if suffix:
            self.api.chroot(suffix)

    def __str__(self):
        return '%s %s' % (str(type(self)), self.api)

    def get(self, suffix='', headers={}):
        return self.api.get(suffix, headers)
