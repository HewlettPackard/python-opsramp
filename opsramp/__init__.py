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
import warnings
import sys
if sys.version_info < (3,):
    warnings.warn(
        "Python 2 reached the end of its life at the end of 2019.\n"
        "Please move to Python 3 because this module will drop support "
        "on {eod}.".format(
            eod='31-Jan-2021'
        ), UserWarning)
