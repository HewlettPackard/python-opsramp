#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# base.py
# Containing various base classes used in other parts of the library
# but not intended for direct use by callers.
#
# (c) Copyright 2019-2020 Hewlett Packard Enterprise Development LP
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
try:
    # Python 3
    from urllib import parse as urlparse
    from simplejson.errors import JSONDecodeError
except ImportError:
    # Python 2
    import urlparse
    JSONDecodeError = ValueError


class Helpers(object):
    # (DW) Add support for retries of requests to the OpsRamp API in the event
    # of receiving a HTTP 429 (Too Many Requests) response from the API to
    # suggest that it has activated rate limiting. This implements progressive
    # backoff (i.e. gradually increasing the delay between attempts) until the
    # maximum number of retries is reached.
    # By wrapping this retry handler around the session instance being used
    # inside instances of the ApiWrapper class the effect of this should be
    # more or less transparent to the rest of the code; at least until rate
    # limiting kicks in, at which point it will hopefully slow down but still
    # "get there" so to speak, and seems to be non-"hacky".
    # The defaults *should* be sensible.
    # Note: if the status_forcelist tuple only has one value (e.g 429) then a
    # trailing comma is REQUIRED for Python to interpret it correctly as a
    # tuple: type((429)) is 'int', whereas type((429,)) is 'tuple'.
    # Borrowed from:
    # https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    @staticmethod
    def session_add_retry_handler(
        retries=7, backoff_factor=1, status_forcelist=(429,), session=None
    ):
        session = session or requests.Session()
        retry = Helpers.create_retry_handler(
            retries, backoff_factor, status_forcelist
        )

        adapter = requests.adapters.HTTPAdapter(max_retries=retry)

        session.mount(prefix='http://', adapter=adapter)
        session.mount(prefix='https://', adapter=adapter)
        return session

    @staticmethod
    def create_retry_handler(retries, backoff_factor, status_forcelist):
        assert isinstance(retries, int)
        assert retries >= 1
        assert backoff_factor > 0
        assert isinstance(status_forcelist, tuple)

        return requests.packages.urllib3.util.retry.Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist
        )


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

    def cd(self, path=None):
        path = str(path or '/')
        # no support for '..' right now, maybe in the future
        if path[0] == '/':
            self.prefix = path
        else:
            self.prefix += '/' + path
        self.prefix = self.prefix.strip('/')
        return self.prefix

    def pushd(self, path=None):
        self.stack.append(self.prefix)
        return self.cd(path)

    def popd(self):
        self.prefix = self.stack.pop()
        return self.prefix

    def fullpath(self, suffix=None):
        suffix = str(suffix or '')
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
    def __init__(self, url, auth, tracker=None, session=None):
        self.baseurl = url.rstrip('/')
        self.auth = auth
        if tracker:
            self.tracker = tracker
        else:
            self.tracker = PathTracker()

        self.session = Helpers.session_add_retry_handler(session=session)

    def __str__(self):
        return '%s "%s" "%s"' % (
            str(type(self)), self.baseurl, self.tracker.fullpath()
        )

    def clone(self):
        new1 = ApiObject(
            self.baseurl,
            self.auth,
            self.tracker.clone(),
            self.session
        )
        return new1

    def cd(self, path=None):
        self.tracker.cd(path)
        return self.compute_url()

    def pushd(self, path=None):
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

    def collate_pages(self, get_request, data):
        """Given a GET request whose results span across multiple pages, crawl
        each page and collate the results.

        :param first_page_data: "results" dict for first pageful of data
        :type first_page_data: dict
        :param request: Request used to get first page
        :type request: requests.PreparedRequest
        """
        # First, sanity check that all is good. Only process GET requests:
        if get_request.method.upper().strip() != "GET":
            return data

        # Only attempt to pull subsequent pages if we can verify that there are
        # subsequent pages "to be pulled"...
        if isinstance(data, dict) and "results" in data.keys():
            collated_data = data["results"]
            while "nextPage" in data.keys() and data["nextPage"]:
                # Get the next page full of data.
                next_page = self.session.get(
                    get_request.url,
                    params={'pageNo': int(data['pageNo']) + 1},
                    headers=get_request.headers
                )

                if not next_page.ok:
                    # Return an empty result.
                    collated_data = []
                    break

                data = next_page.json()
                collated_data = collated_data + data['results']
                del next_page

            # Dismantle the URL to see if data was requested in descending
            # order...
            query_params = dict(
                urlparse.parse_qsl(urlparse.urlsplit(get_request.url).query)
            )
            descending_order = 'isDescendingOrder' in query_params.keys() and \
                query_params['isDescendingOrder']

            # Re-create the final data set as if it were a single page
            # containing all records to ensure that existing stuff that expects
            # this data structure doesn't fall over.
            return {
                'results': collated_data,
                'totalResults': len(collated_data),
                'pageNo': 1,
                'pageSize': len(collated_data),
                'nextPage': False,
                'previousPageNo': 0,
                'descendingOrder': descending_order
            }
        else:
            return data

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

    def process_result(self, url, resp):
        if resp.status_code != requests.codes.OK:
            msg = '%s %s %s %s' % (
                resp,
                resp.request.method,
                url,
                resp.content
            )
            raise RuntimeError(msg)
        try:
            data = resp.json()
            # Some GET requests return paginated output. If all the data fits
            # in one page, return just the contents of the "results" list,
            # otherwise, we need to do an assembly job to collate the entire
            # list of results from all pages and return the full list.
            if resp.request.method == "GET" and isinstance(data, dict) and \
                    data.get("nextPage", None):
                return self.collate_pages(resp.request, data=data)
            else:
                return data
        except JSONDecodeError:
            return resp.text

    def get(self, suffix=None, headers=None):
        url = self.compute_url(suffix)
        hdr = self.prep_headers(headers)
        resp = self.session.get(url, headers=hdr)
        return self.process_result(url, resp)

    def post(self, suffix=None, headers=None, data=None, json=None):
        url = self.compute_url(suffix)
        hdr = self.prep_headers(headers)
        resp = self.session.post(url, headers=hdr, data=data, json=json)
        return self.process_result(url, resp)

    def put(self, suffix=None, headers=None, data=None, json=None):
        url = self.compute_url(suffix)
        hdr = self.prep_headers(headers)
        resp = self.session.put(url, headers=hdr, data=data, json=json)
        return self.process_result(url, resp)

    def delete(self, suffix=None, headers=None, data=None, json=None):
        url = self.compute_url(suffix)
        hdr = self.prep_headers(headers)
        resp = self.session.delete(url, headers=hdr, data=data, json=json)
        return self.process_result(url, resp)

    def patch(self, suffix=None, headers=None, data=None, json=None):
        url = self.compute_url(suffix)
        hdr = self.prep_headers(headers)
        resp = self.session.patch(url, headers=hdr, data=data, json=json)
        return self.process_result(url, resp)


class ApiWrapper(object):
    def __init__(self, apiobject, suffix=None):
        self.api = apiobject.clone()
        if suffix:
            self.api.chroot(suffix)

    def __str__(self):
        return '%s %s' % (str(type(self)), self.api)

    def get(self, suffix=None, headers=None):
        return self.api.get(suffix, headers=headers)
