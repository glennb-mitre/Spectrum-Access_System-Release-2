# Miniconda Environment Setup
## Bash Shell scripts

**Note: Bash installation scripts are *not* Idempotent**

### Installing Miniconda for Python 3.10
The setup script automatically installs Miniconda with Python 3.10 to
.local/ in your HOME directory and configures your shell to automatically
setup Miniconda.

```bash
bash ./setup-conda-3.10.sh -h
Usage: ./setup-conda-3.10.sh -d <Path to Common-Data> (Default: /usr/local/src/winnf/Common-Data/)
            -p <Path to Miniconda environment> (Default: /home/glennb/.local/miniconda3)
            -s <Path to base source directory (e.g., src)

./setup-conda-3.10.sh
```
If your base source directory is not specified on the command line, the script will prompt for the source directory.

When promoted, enter the base directory of where you want to clone the source code.

Example: *src* would put the source code in *$HOME/***src***/winnf/...*

### Activate the sas-2 developer environment.
Ensure the sas-2 conda environment is active.

You must be in the (base) environment before running this command. You may need to restart your terminal.

```bash
conda activate sas-2
```

You should now see (sas-2) preceding your bash command prompt.

The sas-2 environment should now be configured for use.
To review the environment configuration, run...

```bash
conda list
```

Alternatively, the sas-2 environment configuration can be reviewed in [environment.yml](./environment.yml)

### Uninstalling Miniconda3

**Warning:** *This script will uninstall Miniconda3 and all configurations. To remove specific environments,
refer to **Important Miniconda Commands** below.*

```bash
bash ./uninstall-conda.sh 
This will remove all Miniconda installations and environments. Are you sure? [YES|no] YES

Remove conda initialization from .bashrc
Removing /home/glennb/.local/miniconda3 /home/glennb/.conda /home/glennb/.condarc
```

## Important Miniconda Commands
These are useful commands for maintaining a Miniconda environment once it's installed.

### Remove a Miniconda environment

```bash
conda deactivate
conda remove --name sas-2 --all
```

### Create the sas-2 Miniconda environment
**Note:** *Miniconda3 must already be installed*

```bash
cd Spectrum-Access_System-Release-2/src/conda-config
conda env create -f environment.yml
```

### Upgrade the sas-2 Miniconda environment
**Note:** *This upgrades the sas-2 environment from an updated environment.yml configuration file.*
```bash
cd Spectrum-Access_System-Release-2
git pull
cd src/conda-config
conda env update --file environment.yml  --prune
```

### Build an updated environment.yml file
**Note:** *This is useful to bring the environment.yml file back up to date after package maintenance.*

```bash
cd Spectrum-Access_System-Release-2
conda env export | grep -v "^prefix" >environment.yml
git commit environment.yml
git push origin <branch>
```