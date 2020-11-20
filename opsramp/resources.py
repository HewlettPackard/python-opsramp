#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# resources.py
# Resource classes.
#
# (c) Copyright 2020 Hewlett Packard Enterprise Development LP
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
from opsramp.api import ORapi


def list2ormp(result_obj):
    '''Bizarrely, OpsRamp sometimes returns a simple list for
    Resources API calls instead of its usual results struct.'''
    if isinstance(result_obj, dict):
        assert 'results' in result_obj
        assert 'totalResults' in result_obj
        return result_obj
    # Wrap it up in a fake of the typical OpsRamp results struct
    # so that callers don't have to special case it.
    assert isinstance(result_obj, list)
    count = len(result_obj)
    retval = {
        'totalResults': count,
        'pageSize': count,
        'totalPages': 1,
        'pageNo': 1,
        'previousPageNo': 0,
        'nextPage': False,
        'descendingOrder': False,
        'results': result_obj
    }
    return retval


class Resources(ORapi):
    def __init__(self, parent):
        super(Resources, self).__init__(parent.api, 'resources')

    def create(self, definition):
        url_suffix = ''
        return self.api.post(url_suffix, json=definition)

    def update(self, uuid, definition):
        url_suffix = uuid
        return self.api.post(url_suffix, json=definition)

    def delete(self, uuid):
        url_suffix = uuid
        return self.api.delete(url_suffix)

    def search(self, pattern=''):
        '''returns *verbose* details about resources on this tenant'''
        simple_list = super(Resources, self).search(
            pattern=pattern,
            suffix='search'
        )
        return list2ormp(simple_list)

    def minimal(self, pattern=''):
        '''returns *minimal* details about resources on this tenant'''
        simple_list = super(Resources, self).search(
            pattern=pattern,
            suffix='minimal'
        )
        return list2ormp(simple_list)

    def applications(self, uuid):
        url_suffix = '{0}/applications'.format(uuid)
        simple_list = self.api.get(url_suffix)
        return list2ormp(simple_list)

    def availability(self, uuid, start_epoch, end_epoch):
        url_suffix = '{0}/availability?startTime={1}&endTime={2}'.format(
            uuid, start_epoch, end_epoch
        )
        return self.api.get(url_suffix)

    def get_templates(self, uuid, pattern=''):
        url_suffix = '{0}/templates/search?{1}'.format(
            uuid, pattern
        )
        return self.api.get(url_suffix)
