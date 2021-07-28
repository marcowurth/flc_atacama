
## Installation instructions:

1. Go into the folder scripts and run _python setup_paths.py_ to create all necessary folders

2. Copy the path that was printed in 1) as base_path into download_abi.py and plot_abi.py

3. Make sure all the needed python packages are installed. I recommend an separate Miniconda environment with Python 3.9 and the latest versions of the following packages and its dependencies from the conda-forge channel:
numpy, xarray, netcdf4, matplotlib, cartopy, pyproj, xesmf, pillow, palettable, distributed, boto3

   Example package installation instructions:
   * _conda create -n flc_atacama python=3.9_
   * _conda activate flc_atacama_
   * _conda install -c conda-forge numpy xarray netcdf4 matplotlib cartopy pyproj xesmf pillow palettable distributed boto3_

4. As described in download_abi.py put your two AWS keys into the file .aws/credentials and set the AWS region to us-east-1 in the file .aws/config


## Usage:

Only download_abi.py and plot_abi.py are scripts and made to run from the terminal, all the other files are modules containing functions and do nothing if run from the terminal.
