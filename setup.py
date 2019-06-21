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

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='python-opsramp',
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    author='HPE Greenlake Talos',
    author_email='mercury.opsauto@hpe.com',
    description='Python language binding for the Opsramp API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='opsramp',
    url='https://github.com/HewlettPackard/python-opsramp',
    license='Apache 2.0',
    packages=setuptools.find_packages(exclude=['contrib', 'docs', 'tests']),
    classifiers=[
        'Development Status :: 4 - Beta ',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Operating System :: OS Independent',
    ],
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'ormpcli=opsramp.cli:main',
        ],
    },

)
