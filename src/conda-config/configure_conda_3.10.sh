#!/usr/bin/env bash
#    Copyright 2023 SAS Release 2 Project Authors. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

# Script to configure Conda environment for Spectrum Access Systems Release 2 development

# Varify the active environment
conda_env=$(conda info | grep "active environment" | awk -F' : ' '{print $2}')
if [ "${conda_env}" != "sas-2" ]; then
    echo "Conda Environment not correctly set up"
    exit 1
fi

# Install reference models and libs
conda install -y numpy

# Install test harness packages
conda install -y pycurl
conda install -y cryptography
conda install -y pyopenssl

# Install common-data packages
conda install -y six
conda install -y shapely
conda install -y pykml
conda install -y gdal
pip3 install cmake
