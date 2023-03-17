# Miniconda Environment Setup
## Bash Shell scripts

**Note: Bash installation scripts are *not* Idempotent**

### Installing Miniconda for Python 3.10
The setup script automatically installs Miniconda with Python 3.710 to
.local/ in your HOME directory and configures your shell to automatically
setup Miniconda.

```bash
./setup-conda-3.10.sh
```

### Configure the Spectrum Access System Release 2 developer environment
Ensure the sas-2 conda environment is active.

You must be in the (base) environment before running this command. You may need to restart your terminal.

```bash
conda activate sas-2
```

You should now see (sas-2) preceding your bash command prompt.

Run the script to configure the Spectrum Access System release 12 environment. When prompted,
enter the base directory of where you want to clone the source code.

Example: *src* would put the source code in *$HOME/***src***/winnf/...*

```bash
./configure_conda_sas-2.sh
```

### Installed Packages
**General reference models and libs:**

| Package | Description                                                           | Install |
|---------|-----------------------------------------------------------------------|---------|
| numpty | matlab-like numerical maths                                           | Conda |

**Test Harness packages:**

| Package | Description                                                           | Install |
|---------|-----------------------------------------------------------------------|---------|
| pycurl | A Python Interface To The cURL library | Conda |
| cryptography | Cryptographic recipes and primitives | Conda |
| pyopenssl | Python wrapper module around the OpenSSL library | Conda |

**Common Data Packages**

| Package | Description                                      | Install |
|---------|--------------------------------------------------|---------|
| six     | Python 2 and 3 compatibility utilities           | pip3    |
| shapely | Manipulation and analysis of geometric objects                        | Conda   |
| pykml | Python Keyhole Markup Language (KML) library                          | Conda   |
| gdal | Geospatial Data Abstraction Library                                   | Conda   |
| Cmake   | CMake is an open-source, cross-platform family of tools<br/>designed to build, test and package software | pip3    |
| winnf   | Wireless Innovation Forum Common Data utililties | pip3    |