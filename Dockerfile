# A sample Dockerfile to build a container for running the CLI example
# tool that comes with this package. You can use "docker run -ti" to
# start this container interactively and use -e to pass in the environment
# variables it needs (see cli.py). Once inside you can run commands like:
#
# ormpcli tenant rba categories
# ormpcli tenant agent script
# ormpcli tenant monitoring templates
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
#
FROM python:3.7.3-slim as build
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*
# use artifact from previous build step in pipeline
ADD . /build
RUN pip install /build

FROM python:3.7.3-slim as prod
LABEL description="OpsRamp CLI"
LABEL maintainer "HPE Greenlake Talos <mercury.opsauto@hpe.com>"
COPY --from=build /usr/local /usr/local

ENTRYPOINT ["/bin/bash"]
