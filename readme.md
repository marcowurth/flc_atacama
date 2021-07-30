
## Installation instructions
1. After cloning or unzipping the repo cd with a terminal into the folder scripts and run _python setup_paths.py_ to create all necessary folders

2. Copy the path that was printed in 1) as base_path into the empty strings at the beginnings of download_abi.py and plot_abi.py

3. Make sure all the needed python packages are installed. I recommend an separate Miniconda environment with Python 3.9 and the latest versions of the following packages and its dependencies from the conda-forge channel:
numpy, xarray, netcdf4, matplotlib, cartopy, pyproj, xesmf, pillow, palettable, distributed, boto3

   Example package installation instructions:
   * _conda create -n flc_atacama python=3.9_
   * _conda activate flc_atacama_
   * _conda install -c conda-forge numpy xarray netcdf4 matplotlib cartopy pyproj xesmf pillow palettable distributed boto3_


## Parallelized Downloading
With the serial download setting I get a mean speed of around 3.5 files/min of the L2-CMIPF 2km bands (including the time needed for the region cropping done by the script). With the parallelized downloading setting however I get a mean speed of around 40-45 files/min of the same files. Unfortunately parallelized downloading won't work without AWS credentials, at least I couldn't make it work.

#### How to get your AWS Credentials
1. If you don't have already an AWS account you will have to open one under [https://aws.amazon.com](https://aws.amazon.com) -> Create an AWS Account. You will need to give your address, number and credit card information even if you'll never use a non-free service. Don't be confused by a 12-month free period, it won't cost you anything to download GOES data afterwards. Every new AWS account can use some AWS services for 12 months for free that instead would cost money. Downloading ABI data from the Amazon S3 bucket _noaa-goes16_ is free always as the data is public.
2. Log into as root user under [https://console.aws.amazon.com](https://console.aws.amazon.com), switch to English and head on the right top under your account name to "My Security Credentials". There under "Access keys" create a new key pair and save it as a local file somewhere.
3. [Install the AWS CLI version 2 on your system](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html). Test it with _aws --version_.
4. Run _aws configure_ and fill in the two keys you saved earlier. Fill in _us-east-1_ as region an _text_ as output format. This should under Linux create a hidden folder in your home directory called .aws where this settings are stored and later read when downloading GOES data in parallel.

## Some Information about all the freely available GOES data on Amazon S3:
[https://docs.opendata.aws/noaa-goes16/cics-readme.html](https://docs.opendata.aws/noaa-goes16/cics-readme.html)



## Code Usage
Only download_abi.py and plot_abi.py int the goes folder are scripts and made to run from the terminal, all the other files are modules containing functions and do nothing if run from the terminal.
