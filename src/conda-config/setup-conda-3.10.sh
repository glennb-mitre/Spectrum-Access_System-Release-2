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
# Installs and configures Miniconda for Spectrum Access System, Release 2 development
# This script is not idempotent. It should only be run once to install Miniconda3.

# Provide a usage statement for the setup script
usage(){
    cat << EOF
Usage: ${0} -d <Path to Common-Data> (Default: /usr/local/src/winnf/Common-Data/)
            -p <Path to Miniconda environment> (Default: ${HOME}/.local/miniconda3)
            -s <Path to base source directory (e.g., src)
EOF
    exit 1
}

# Script default paths
# Path where the Common-Data repository is installed, changed with the -d option
DATADIR="/usr/local/src/winnf/Common-Data/"
# Miniconda installation package. Modifying this requires an update to SHA256SUMS.
conda_exe="Miniconda3-py310_23.1.0-1-Linux-x86_64.sh"
# Miniconda environment path, changed with -p option
conda_path="${HOME}/.local/miniconda3"
# A local temp directory for file downloads
tmp_dir=./tmp

# Process command line options
while getopts "c:d:p:s:h" opt; do
    case ${opt} in
        d) DATADIR=${OPTARG}
           ;;
        p) conda_path=${OPTARG}
           ;;
        s) SRCDIR=${OPTARG}
           ;;
        h) usage
           ;;
        *) usage
           ;;
    esac
done
shift $((OPTIND-1))

pushd .
if [ ! -d ${tmp_dir} ]; then
    mkdir ${tmp_dir}
fi

# Get miniconda installer and verify download
if [ ! -f "${tmp_dir}/${conda_exe}" ]; then
    cd ${tmp_dir} && wget "https://repo.anaconda.com/miniconda/${conda_exe}"
else
    cd ${tmp_dir} || exit
fi
sha256sum -c ../SHA256SUMS || exit 1

# Install Miniconda
# Check if the install path exists and request upgrade if it does
if [ -d "${conda_path}" ]; then
    # shellcheck disable=SC2162
    read -r -p "${conda_path} exists, Upgrade Miniconda? [Y/N]" query
    if [ "$query" == "Y" ] || [ "$query" == "y" ]; then
        /usr/bin/bash ${conda_exe} -u -p "${conda_path}"
    else
        echo "Miniconda not upgraded, exiting"
        exit 1
    fi
else
    /usr/bin/bash ${conda_exe} -b -p "${conda_path}"
fi
source "${conda_path}/bin/activate"
conda init

# Link Common Data Repository
if [ -z "${SRCDIR}" ]; then
    read -r -p "Enter source directory root (e.g. src): " SRCDIR
fi
if [ ! -d "${HOME}/${SRCDIR}/winnf" ]; then
    mkdir -p "${HOME}/${SRCDIR}/winnf" || exit 9
fi
cd "${HOME}/${SRCDIR}/winnf" || exit 9

# Set up links to common data
if [ ! -L "${DATADIR}" ]; then
    ln -sf "${DATADIR}" ./Common-Data
fi

# Create the miniconda sas-2 environment
# Install Conda modules into the base environment
popd
conda env create --file environment.yml

echo "Close and Re-Open your terminal window and run:"
echo "conda activate sas-2"
