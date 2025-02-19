#!/usr/bin/env python
#
# (c) Copyright 2020-2025 Hewlett Packard Enterprise Development LP
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

import unittest

import opsramp.binding
import requests_mock


class KBtest(unittest.TestCase):
    def setUp(self):
        fake_url = "mock://api.example.com"
        fake_token = "unit-test-fake-token"
        self.ormp = opsramp.binding.Opsramp(fake_url, fake_token)

        self.fake_client_id = "client_for_unit_test"
        self.client = self.ormp.tenant(self.fake_client_id)
        assert self.client.is_client()

        self.kb = self.client.kb()
        assert "KnowledgeBase" in str(self.kb)


class CategoriesTest(KBtest):
    def setUp(self):
        super(CategoriesTest, self).setUp()
        self.categories = self.kb.categories()
        assert "KBcategories" in str(self.categories)

    def test_create(self):
        group = self.categories
        url = group.api.compute_url("create")
        expected = {"id": 345678}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected, complete_qs=True)
            actual = group.create(definition=expected)
        assert actual == expected

    def test_update(self):
        group = self.categories
        thisid = 123456
        url = group.api.compute_url("update/%s" % thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected, complete_qs=True)
            actual = group.update(uuid=thisid, definition=expected)
        assert actual == expected

    def test_delete(self):
        group = self.categories
        thisid = 789012
        url = group.api.compute_url("delete/%s" % thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.delete(url, json=expected, complete_qs=True)
            actual = group.delete(uuid=thisid)
        assert actual == expected

    def test_restore(self):
        group = self.categories
        thisid = 345678
        url = group.api.compute_url("restore/%s" % thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected, complete_qs=True)
            actual = group.restore(uuid=thisid)
        assert actual == expected

    def test_get_id(self):
        group = self.categories
        thisid = 345678
        url = group.api.compute_url(thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            m.get(url, json=expected, complete_qs=True)
            actual = group.get(thisid)
            assert actual == expected

    def test_children(self):
        group = self.categories
        thisid = 901234
        # searches happen at the "kb" level
        url = self.kb.api.compute_url("categorylist/%s" % thisid)
        expected = ["unit", "test", "list"]
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected, complete_qs=True)
            actual = group.children(thisid)
        assert actual == expected

    def test_search(self):
        group = self.categories
        pattern = "whatever"
        # searches happen at the "kb" level
        url = self.kb.api.compute_url("categorylist?%s" % pattern)
        expected = ["unit", "test", "list"]
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected, complete_qs=True)
            actual = group.search(pattern=pattern)
        assert actual == expected


class ArticlesTest(KBtest):
    def setUp(self):
        super(ArticlesTest, self).setUp()
        self.articles = self.kb.articles()
        assert "KBarticles" in str(self.articles)

    def test_create(self):
        group = self.articles
        url = group.api.compute_url()
        expected = {"id": 345678}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected, complete_qs=True)
            actual = group.create(definition=expected)
        assert actual == expected

    def test_update(self):
        group = self.articles
        thisid = 123456
        url = group.api.compute_url("%s" % thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected, complete_qs=True)
            actual = group.update(uuid=thisid, definition=expected)
        assert actual == expected

    def test_delete(self):
        group = self.articles
        thisid = 789012
        url = group.api.compute_url("%s/delete" % thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.delete(url, json=expected, complete_qs=True)
            actual = group.delete(uuid=thisid)
        assert actual == expected

    def test_share(self):
        group = self.articles
        thisid = 789012
        url = group.api.compute_url("%s/share" % thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected, complete_qs=True)
            actual = group.share(uuid=thisid, definition=expected)
        assert actual == expected

    def test_get_id(self):
        group = self.articles
        thisid = 345678
        url = group.api.compute_url(thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            m.get(url, json=expected, complete_qs=True)
            actual = group.get(thisid)
            assert actual == expected

    def test_comments(self):
        group = self.articles
        thisid = 567890
        url = group.api.compute_url("%s/comments/" % thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            m.get(url, json=expected, complete_qs=True)
            actual = group.comments(thisid)
            assert actual == expected

    def test_search(self):
        group = self.articles
        pattern = "whatever"
        # searches happen at the "kb" level
        url = self.kb.api.compute_url("articlesList?%s" % pattern)
        expected = ["unit", "test", "list"]
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected, complete_qs=True)
            actual = group.search(pattern)
        assert actual == expected


class TemplatesTest(KBtest):
    def setUp(self):
        super(TemplatesTest, self).setUp()
        self.templates = self.kb.templates()
        assert "KBtemplates" in str(self.templates)

    def test_create(self):
        group = self.templates
        url = group.api.compute_url()
        expected = {"id": 345678}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected, complete_qs=True)
            actual = group.create(definition=expected)
        assert actual == expected

    def test_update(self):
        group = self.templates
        thisid = 123456
        url = group.api.compute_url("%s" % thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.post(url, json=expected, complete_qs=True)
            actual = group.update(uuid=thisid, definition=expected)
        assert actual == expected

    def test_delete(self):
        group = self.templates
        thisid = 789012
        url = group.api.compute_url("%s/delete" % thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            assert expected
            m.delete(url, json=expected, complete_qs=True)
            actual = group.delete(uuid=thisid)
        assert actual == expected

    def test_get_id(self):
        group = self.templates
        thisid = 345678
        url = group.api.compute_url(thisid)
        expected = {"id": thisid}
        with requests_mock.Mocker() as m:
            m.get(url, json=expected, complete_qs=True)
            actual = group.get(thisid)
            assert actual == expected

    def test_search(self):
        group = self.templates
        pattern = "whatever"
        # searches happen at the "kb" level
        url = self.kb.api.compute_url("templatesList?%s" % pattern)
        expected = ["unit", "test", "list"]
        with requests_mock.Mocker() as m:
            assert expected
            m.get(url, json=expected, complete_qs=True)
            actual = group.search(pattern=pattern)
        assert actual == expected
