#!/usr/bin/env python
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
import unittest

import opsramp.binding


class TrackerTest(unittest.TestCase):
    def setUp(self):
        self.trkr = opsramp.binding.PathTracker()

    def test_cd(self):
        progression = (
            ('/tmp', '/tmp'),
            ('bossa', '/tmp/bossa'),
            ('nova', '/tmp/bossa/nova'),
            ('george/dragon', '/tmp/bossa/nova/george/dragon'),
            ('/wardrobe/narnia', '/wardrobe/narnia'),
            ('/', '')
        )
        for pshort, pfull in progression:
            self.trkr.cd(pshort)
            self.assertEqual(self.trkr.fullpath(), pfull)

    def test_pushpop(self):
        self.trkr.cd('/themoon')
        home = self.trkr.fullpath()

        city = '/europe/germany/berlin'
        street = 'Alexanderplatz'
        both = city + '/' + street

        a_pushd = 1
        a_popd = 2
        progression = (
            (a_pushd, city, city),
            (a_pushd, street, both),
            (a_popd, None, city),
            (a_pushd, street, both),
            (a_pushd, '/logs', '/logs'),
            (a_popd, None, both),
            (a_popd, None, city),
            (a_popd, None, home)
        )
        self.assertEqual(self.trkr.fullpath(), home)
        for action, pshort, pfull in progression:
            if action == a_pushd:
                self.trkr.pushd(pshort)
            elif action == a_popd:
                assert not pshort
                self.trkr.popd()
            else:
                assert False
            self.assertEqual(self.trkr.fullpath(), pfull)
