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

# Script to uninstall Miniconda

conda_dirs="${HOME}/.local/miniconda3 ${HOME}/miniconda3 ${HOME}/.conda ${HOME}/.condarc"

read -r -p "This will remove all Miniconda installations and environments. Are you sure? [YES|no] " query
if [ "${query}" == "YES" ]; then
    # Remove conda initialization from .bashrc
    sed -i '/# >>> conda initialize >>>/,/# <<< conda initialize <<</d' "${HOME}/.bashrc"

    # Remove the conda environment
    for conda in ${conda_dirs}; do
        if [ -d "${conda}" ]; then
            rm -rf "${conda}"
        fi
    done
fi