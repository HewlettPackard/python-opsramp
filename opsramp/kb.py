#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# kb.py
# Classes dealing directly with OpsRamp knowledge base categories
# and articles.
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


class KnowledgeBase(ORapi):
    def __init__(self, parent):
        super(KnowledgeBase, self).__init__(parent.api, 'kb')

    def categories(self):
        return KBcategories(self)

    def articles(self):
        return KBarticles(self)

    def templates(self):
        return KBtemplates(self)


class KBcategories(ORapi):
    def __init__(self, parent):
        super(KBcategories, self).__init__(parent.api, 'category')
        # weirdly, calls to "categorylist" need to be made at "kb" level
        # so we need to keep a handle on the parent object's API.
        self.parent_api = parent.api.clone()

    def create(self, definition):
        resp = self.api.post('create', json=definition)
        return resp

    def update(self, uuid, definition):
        return self.api.post('update/%s' % uuid, json=definition)

    def delete(self, uuid):
        return self.api.delete('delete/%s' % uuid)

    def search(self, pattern=''):
        suffix = 'categorylist'
        if pattern:
            suffix += '?' + pattern
        # weirdly, this call needs to be made at "kb" level
        return self.parent_api.get(suffix)

    def children(self, uuid):
        assert uuid
        suffix = 'categorylist/%s' % uuid
        # weirdly, this call needs to be made at "kb" level
        return self.parent_api.get(suffix)

    def restore(self, uuid):
        return self.api.post('restore/%s' % uuid)


class KBarticles(ORapi):
    def __init__(self, parent):
        super(KBarticles, self).__init__(parent.api, 'article')
        # weirdly, calls to "articlesList" need to be made at "kb" level
        # so we need to keep a handle on the parent object's API.
        self.parent_api = parent.api.clone()

    def create(self, definition):
        resp = self.api.post(json=definition)
        return resp

    def update(self, uuid, definition):
        return self.api.post('%s' % uuid, json=definition)

    def delete(self, uuid):
        return self.api.delete('%s/delete' % uuid)

    def search(self, pattern=''):
        suffix = 'articles/search'
        if pattern:
            suffix += '?' + pattern
        # weirdly, this call needs to be made at "kb" level
        return self.parent_api.get(suffix)

    def share(self, uuid, definition):
        return self.api.post('%s/share' % uuid, json=definition)

    def comments(self, uuid):
        return self.api.get('%s/comments' % uuid)


class KBtemplates(ORapi):
    def __init__(self, parent):
        super(KBtemplates, self).__init__(parent.api, 'template')
        # weirdly, calls to "templatesList" need to be made at "kb" level
        # so we need to keep a handle on the parent object's API.
        self.parent_api = parent.api.clone()

    def create(self, definition):
        resp = self.api.post(json=definition)
        return resp

    def update(self, uuid, definition):
        return self.api.post('%s' % uuid, json=definition)

    def delete(self, uuid):
        return self.api.delete('%s/delete' % uuid)

    def search(self, pattern=''):
        suffix = 'templatesList'
        if pattern:
            suffix += '?' + pattern
        # this call needs to be made at "kb" level
        return self.parent_api.get(suffix)
