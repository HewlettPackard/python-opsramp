#!/usr/bin/env python
#
# (c) Copyright 2019-2021 Hewlett Packard Enterprise Development LP
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

from opsramp.base import PathTracker


class TrackerTest(unittest.TestCase):
    def setUp(self):
        self.trkr = PathTracker()
        assert 'PathTracker' in str(self.trkr)

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
            assert self.trkr.fullpath() == pfull

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
        assert self.trkr.fullpath() == home
        for action, pshort, pfull in progression:
            if action == a_pushd:
                self.trkr.pushd(pshort)
            elif action == a_popd:
                assert not pshort
                self.trkr.popd()
            else:
                raise AssertionError('unexpected action %s' % action)
            assert self.trkr.fullpath() == pfull

    def test_reset(self):
        self.trkr.cd('/solarsystems/milkyway')
        self.trkr.reset()
        assert self.trkr.fullpath() == ''

    def test_clone(self):
        place1 = '/saturn/atmosphere'
        self.trkr.cd(place1)
        # check that cd in a clone doesn't affect the original.
        other = self.trkr.clone()
        place2 = '/jupiter/satellites/moons/ganymede'
        other.cd(place2)
        assert self.trkr.fullpath() == place1
        assert other.fullpath() == place2

    def test_fullpath(self):
        # check that it doesn't "cd" to the specified suffix, just appends it.
        self.trkr.cd('my/hovercraft')
        original = self.trkr.fullpath()
        suffix = 'is/full/of/eels'
        other = self.trkr.fullpath(suffix)
        assert other == original + '/' + suffix
        assert self.trkr.fullpath() == original
        # test with a / at the start, which should not append (nor cd there).
        suffix = '/full/path/not/relative'
        other = self.trkr.fullpath(suffix)
        assert other == suffix
        assert self.trkr.fullpath() == original
