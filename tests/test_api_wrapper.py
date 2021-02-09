#!/usr/bin/env python
#
# (c) Copyright 2020-2021 Hewlett Packard Enterprise Development LP
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
from mock import MagicMock

from opsramp.base import ApiWrapper


class ClassTest(unittest.TestCase):
    def setUp(self):
        self.mock_ao = MagicMock()
        self.mock_ao.clone.return_value = self.mock_ao
        self.testobj = ApiWrapper(self.mock_ao)

    def test_str(self):
        assert 'ApiWrapper' in str(self.testobj)

    def test_session_property(self):
        aw = self.testobj
        original_session = aw.session
        assert original_session
        # test the setter and getter
        fake_session = MagicMock()
        aw.session = fake_session
        assert aw.session is fake_session
        # put the real one back
        aw.session = original_session
        assert aw.session is original_session

    def test_get(self):
        ut_hdrs = {'fake-header': 'fake-value'}
        expected = 'unit test get result'
        self.mock_ao.get.return_value = expected

        suffix = 'milk'
        # default headers
        actual = self.testobj.get(suffix)
        self.mock_ao.get.assert_called_with(suffix, headers=None)
        assert actual == expected
        # specific headers
        actual = self.testobj.get(suffix, headers=ut_hdrs)
        self.mock_ao.get.assert_called_with(suffix, headers=ut_hdrs)
        assert actual == expected

    def four_variants(self, suffix, test_fn, mock_ao_fn):
        ut_hdrs = {'fake-header': 'fake-value'}
        ut_text = 'some unit test string'
        ut_json = {'id': 'unit test'}
        expected = 'unit test result'
        mock_ao_fn.return_value = expected

        # all defaults
        actual = test_fn()
        mock_ao_fn.assert_called_with(
            None, headers=None,
            data=None, json=None
        )

        # with suffix
        actual = test_fn(suffix)
        mock_ao_fn.assert_called_with(
            suffix, headers=None,
            data=None, json=None
        )
        # specific headers
        actual = test_fn(suffix, headers=ut_hdrs)
        mock_ao_fn.assert_called_with(
            suffix, headers=ut_hdrs,
            data=None, json=None
        )
        assert actual == expected
        # specific text body
        actual = test_fn(suffix, data=ut_text)
        mock_ao_fn.assert_called_with(
            suffix, headers=None,
            data=ut_text, json=None
        )
        assert actual == expected
        # specific json body
        actual = test_fn(suffix, json=ut_json)
        mock_ao_fn.assert_called_with(
            suffix, headers=None,
            data=None, json=ut_json
        )
        assert actual == expected

    def test_post(self):
        self.four_variants(
            'eggs',
            self.testobj.post,
            self.mock_ao.post
        )

    def test_put(self):
        self.four_variants(
            'flour',
            self.testobj.put,
            self.mock_ao.put
        )

    def test_delete(self):
        self.four_variants(
            'sultanas',
            self.testobj.delete,
            self.mock_ao.delete
        )

    def test_patch(self):
        self.four_variants(
            'meat',
            self.testobj.patch,
            self.mock_ao.patch
        )
