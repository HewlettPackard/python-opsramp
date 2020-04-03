#!/bin/bash
#
# runtests.sh
# This script runs the actual test commands and assumes that the required
# packages are already installed. Installation of the packages is done
# outside of this script using pip install -r test-requirements.txt and
# that command is already folded into our tox.ini
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

set -eux -o pipefail
flake8 --ignore=none --exclude=.git,__pycache__,.tox,.eggs,*.egg,venv,venv2,venv3
coverage run --include='opsramp/*' -m pytest -vvv
coverage report
coverage html
coverage xml -o ./cover/coverage.xml
