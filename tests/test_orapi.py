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
import base64
from mock import MagicMock

from opsramp.api import ORapi


class StaticsTest(unittest.TestCase):
    def check64(self, testfile):
        with open(testfile, 'rb') as f:
            content_raw = f.read()
        content_64 = ORapi.b64encode_payload(testfile)
        # decode this result and check against the actual content.
        decoded = base64.b64decode(content_64)
        return decoded == content_raw

    def test_base64(self):
        # a file that is guaranteed to be empty.
        assert self.check64('/dev/null')
        # any non-empty file that we know will exist.
        assert self.check64('setup.py')


class ClassTest(unittest.TestCase):
    def setUp(self):
        self.mock_ao = MagicMock()
        self.mock_ao.clone.return_value = self.mock_ao
        self.testobj = ORapi(self.mock_ao)

    def test_str(self):
        assert 'ORapi' in str(self.testobj)

    def test_session_property(self):
        # The session property is defined in the base class but we
        # will unit test it here anyway, to make sure nobody changes
        # the base class in a way that breaks us.
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
        hdrs = {'fake-header': 'fake-value'}
        expected = 'unit test get result'
        self.mock_ao.get.return_value = expected

        suffix = 'milk'
        actual = self.testobj.get(suffix, headers=hdrs)
        self.mock_ao.get.assert_called_with(suffix, headers=hdrs)
        assert actual == expected

    def test_search(self):
        hdrs = {'fake-header': 'fake-value'}
        expected = 'unit test search result'
        self.mock_ao.get.return_value = expected

        # the leading ? character is optional so try both.
        qstring = '?name=marmaduke'
        qs2 = qstring[1:]

        # default suffix should be "search"
        actual = self.testobj.search(pattern=qstring)
        self.mock_ao.get.assert_called_with('search' + qstring, headers=None)
        assert actual == expected
        actual = self.testobj.search(pattern=qs2, headers=hdrs)
        self.mock_ao.get.assert_called_with('search' + qstring, headers=hdrs)
        assert actual == expected

        # try a different suffix
        suffix = 'toraiocht'
        actual = self.testobj.search(pattern=qstring, suffix=suffix)
        self.mock_ao.get.assert_called_with(suffix + qstring, headers=None)
        assert actual == expected
        actual = self.testobj.search(pattern=qs2, headers=hdrs, suffix=suffix)
        self.mock_ao.get.assert_called_with(suffix + qstring, headers=hdrs)
        assert actual == expected
