#!/usr/bin/env python
#
# A minimal Python language binding for the OpsRamp REST API.
#
# first_response.py
# Classes dealing directly with OpsRamp First Response Policies.
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

from opsramp.api import ORapi


class First_Response(ORapi):
    def __init__(self, parent):
        super(First_Response, self).__init__(parent.api,
                                             'policies/firstResponse')

    def search(self, pattern=''):
        return super(First_Response, self).search(
            pattern=pattern,
            suffix=''
        )

    def policy_detail(self, uuid):
        return self.api.get('%s' % uuid)

    def create(self, definition):
        return self.api.post('', json=definition)

    def update(self, uuid, definition):
        return self.api.post('%s' % uuid, json=definition)

    def delete(self, uuid):
        return self.api.delete('%s' % uuid)

    def enable(self, uuid):
        return self.api.post('%s/enable' % uuid)

    def disable(self, uuid):
        return self.api.post('%s/disable' % uuid)


class ModelTraining(ORapi):
    def __init__(self, parent):
        super(ModelTraining, self).__init__(parent.api, 'machineLearning')

    def train_model(self):
        return self.api.post('train/ALERT_FIRST_RESPONSE_TRAINING')

    def file_upload(self, payload, files):
        return self.api.post('files', data=payload, files=files)

    def get_training_file(self):
        return self.api.get('files')
