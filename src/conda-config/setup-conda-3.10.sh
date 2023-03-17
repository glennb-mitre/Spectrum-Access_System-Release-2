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

# Miniconda setup script

conda_exe="Miniconda3-py310_23.1.0-1-Linux-x86_64.sh"
conda_path="${HOME}/.local/miniconda3"
tmp_dir=./tmp

if [ ! -d ${tmp_dir} ]; then
  mkdir ${tmp_dir}
fi

# Get miniconda installer and verify download
if [ ! -f ${tmp_dir}/${conda_exe} ]; then
    cd ${tmp_dir} && wget https://repo.anaconda.com/miniconda/${conda_exe}
else
    cd ${tmp_dir} || exit
fi
sha256sum -c ../SHA256SUMS || exit 1

# Install Miniconda
# Check if the install path exists and request upgrade if it does
if [ -d "${conda_path}" ]; then
  # shellcheck disable=SC2162
  read -p "${conda_path} exists, Upgrade Miniconda? [Y/N]" query
  if [ "$query" == "Y" ] || [ "$query" == "y" ]; then
    /usr/bin/bash ${conda_exe} -u
  else
    echo "Miniconda not upgraded, exiting"
    exit 1
  fi
else
  /usr/bin/bash ${conda_exe} -b -p "${conda_path}"
fi
source "${conda_path}/bin/activate"
conda init

# Install Conda modules into the base environment
# Create the miniconda Python 3.10 Environment
conda create --name sas-2 python=3.10

echo "Close and Re-Open your terminal window and run:"
echo "conda activate sas-2"