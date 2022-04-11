#!/bin/bash
#
# (c) Copyright 2019-2022 Hewlett Packard Enterprise Development LP
#
# runtests.sh
# This script runs the actual test commands and assumes that the required
# packages are already installed. Installation of the packages is done
# outside of this script using pip install -r test-requirements.txt and
# that command is already folded into our tox.ini
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

set -eux -o pipefail
windowsnewlines=$(file */*py | awk '/CRLF/ {print $0}')
if [ -n "$windowsnewlines" ]; then
  echo 'Windows newlines are not allowed in Python sources in this repo' >&2
  exit 1
fi
yamllint .
flake8 .
coverage run --include='opsramp/*' -m pytest -vvv
coverage report
coverage html
coverage xml -o ./cover/coverage.xml
