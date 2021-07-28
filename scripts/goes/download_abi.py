
########################################################################################################################
###                                                                                                                  ###
###  This script uses a width of max. 120 characters                                                                 ###
###                                                                                                                  ###
###  Author: Marco Wurth, July 2021                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: distributed, boto3, xarray, netcdf4                                               ###
###                                                                                                                  ###
###  Any download needs two strings called aws_access_key_id and aws_secret_access_key to be in a file               ###
###   at /home/username/.aws/credentials and also setting the AWS Region to us-east-1 in a file                      ###
###   at /home/username/.aws/config                                                                                  ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   1) Execute in terminal folder>python download_abi.py                                                           ###
###   2) Via import of download_abi_files or download_single_abi_file from another script                            ###
###                                                                                                                  ###
###  Known bugs: There is an issue with boto3 and parallelization that sometimes leads                               ###
###   to KeyError('endpoint_resolver') or KeyError('credential_provider') but if download_retries_per_file > 1       ###
###   it will most probably work on the next retry of the thread and download all files succesfully in the end       ###
###                                                                                                                  ###
########################################################################################################################

import sys
import os
import time
import datetime
import fnmatch

import distributed      # provides parallelization features, see distributed.dask.org/en/latest
import boto3            # provides access to the Amazon Simple Storage Service (Amazon S3)
import xarray as xr     # provides interface for reading, manipulation and writing of netcdf files

base_path = ''
sys.path.append(base_path + 'scripts')


def main():

    # parallelization settings #

    #distributed_exec = False
    distributed_exec = True

    num_max_parallel_tasks = 8
    #num_max_parallel_tasks = 24
    download_retries_per_file = 3


    # specify product #

    product = 'L2-CMIPF'       # Full-disk
    #product = 'L2-CMIPM1'      # Mesoscale Sector 1
    #product = 'L2-CMIPM2'      # Mesoscale Sector 1


    # specify region to be saved at the end, mesoscale sector files are not cut and regions ignored #
    # smaller regions use less disk space #

    #region = 'fulldisk'
    #region = 'ssa'
    #region = 'atacama'
    region = 'atacama_squared'  # this extends the rectangular atacama region to the west and east


    # get latest available image time #

    if product == 'L2-CMIPF':
        timediff_minutes = 20   # if not enough raise to 30min
        datetime_now = datetime.datetime.utcnow()
        datetime_latest = datetime_now - datetime.timedelta(
                            seconds = (datetime_now.minute % 10 + timediff_minutes) * 60 + datetime_now.second)
    elif product == 'L2-CMIPM1' or product == 'L2-CMIPM2':
        timediff_minutes = 2
        datetime_now = datetime.datetime.utcnow()
        datetime_latest = datetime_now - datetime.timedelta(seconds = timediff_minutes * 60 + datetime_now.second)

    print('now:'.ljust(8), datetime_now)
    print('latest:'.ljust(8), datetime_latest)

    year = datetime_latest.year
    month = datetime_latest.month
    days = [datetime_latest.day]
    hours = [datetime_latest.hour]
    minutes = [datetime_latest.minute]


    # override latest time with specified time #

    #year = 2021
    #month = 4
    days = [25]
    #days = list(range(1, 31))
    #hours = list(range(0, 10))
    #hours = list(range(12, 17))
    #minutes = list(range(0, 60, 10))
    hours = [17]
    minutes = [0]


    # specify bands (possible 1-16) to download #

    #bands = [2,5,6,7,8,10,13]
    #bands = [5,6,7,8,10]
    #bands = [13]
    #bands = [2, 3]
    bands = list(range(1, 16+1))


    download_abi_files(base_path, distributed_exec, num_max_parallel_tasks, download_retries_per_file,
                       product, region, bands, year, month, days, hours, minutes)

    return

########################################################################################################################
########################################################################################################################
########################################################################################################################

def download_abi_files(base_path, distributed_exec, num_max_parallel_tasks, download_retries_per_file,
                       product, region, bands, year, month, days, hours, minutes):

    print('load:'.ljust(8), datetime.datetime(year, month, days[0], hours[0], minutes[0]), 'to',
                            datetime.datetime(year, month, days[-1], hours[-1], minutes[-1]),
           'region:', region)
    print('------------------------------------------')


    # parallel execution with dask distributed #

    if distributed_exec:
        client = distributed.Client(n_workers = 1, processes = True, threads_per_worker = num_max_parallel_tasks)
        print(client)

        for day in days:
            date_bands = []
            for hour in hours:
                for minute in minutes:
                    for band in bands:
                        date_bands.append([datetime.datetime(year, month, day, hour, minute), band])
        print('total number of tasks:', len(date_bands))

        sub_date_bands = []
        if num_max_parallel_tasks > len(date_bands):
            num_max_parallel_tasks = len(date_bands)
        for i in range(len(date_bands) // num_max_parallel_tasks):
            sub_date_bands.append(date_bands[i * num_max_parallel_tasks : (i + 1) * num_max_parallel_tasks])
        if len(date_bands) % num_max_parallel_tasks > 0:
            sub_date_bands.append(date_bands[-1 * (len(date_bands) % num_max_parallel_tasks) : ])

        all_tasks = []
        for sub_date_band in sub_date_bands:
            futures = []
            for date_band in sub_date_band:
                futures.append(client.submit(download_single_abi_file, base_path, product, date_band[0], date_band[1],
                                             region, retries = download_retries_per_file))
            distributed.wait(futures)
            all_tasks += futures

        print('------------------------------------------')
        try:
            # uncomment the next three lines to print all filenames #
            #print('all downloaded files:')
            #for f in all_tasks:
            #    print(f.result())

            testlist = [f.result()[-10 - len(region):] for f in all_tasks]
            if testlist.count('region-' + region + '.nc') == len(testlist):
                print('                        #             ')
                print('                     #                ')
                print('                  #                   ')
                print('     #         #                      ')
                print('       #    #                         ')
                print('         #                            ')
                print('                                      ')
                print('all tasks finished successfully       ')

        except:
                print('            #           #             ')
                print('              #       #               ')
                print('                #   #                 ')
                print('                  #                   ')
                print('                #   #                 ')
                print('              #       #               ')
                print('            #           #             ')
                print('                                      ')
                print('some tasks failed and some or all files could probably not be downloaded')

        #client.restart()
        #print('client restarted')

        client.close()


    # serial execution #

    else:
        for day in days:
            for hour in hours:
                for minute in minutes:
                    for band in bands:
                        date_load = datetime.datetime(year, month, day, hour, minute)
                        print('load:'.ljust(8), date_load)
                        download_single_abi_file(base_path, product, date_load, band, region)


    return

############################################################################
############################################################################
############################################################################

def download_single_abi_file(base_path, product_fullname, date, band, region):

    # cut the mesoscale sector number #

    if product_fullname == 'L2-CMIPF':
        product = product_fullname
    elif product_fullname[:-1] == 'L2-CMIPM':
        product = product_fullname[:-1]
        meso_num = int(product_fullname[-1])

    path = dict(base = base_path,
                data = 'data/ABI/GOES-16/{}/'.format(product))


    dayofyear = (date - datetime.datetime(date.year, 1, 1)).days + 1

    subfolder = 'ABI-{}/{:4d}/{:03d}/{:02d}'.format(product, date.year, dayofyear, date.hour)

    match_string = '*{}-M6C{:02d}_G16_s{:4d}{:03d}{:02d}{:02d}*'.format(
                    product_fullname, band, date.year, dayofyear, date.hour, date.minute)

    s3 = boto3.resource('s3')
    noaa_bucket = s3.Bucket('noaa-goes16')
    file_list = []
    for object in noaa_bucket.objects.filter(Prefix = subfolder):
        file_list.append(object.key)
    
    filename = fnmatch.filter(file_list, match_string)[0]
    #print('matched filename')

    obj = noaa_bucket.Object(filename)
    filename = filename[28:]
    with open(path['base'] + path['data'] + 'temp/' + filename, 'wb') as file:
        obj.download_fileobj(file)

    del s3

    if product == 'L2-CMIPF':
        filename_region = cut_file_to_region(path, filename, band, region)
        band_subfolder = 'b{:02d}'.format(band)
        if not band_subfolder in os.listdir(path['base'] + path['data']):
            os.mkdir(path['base'] + path['data'] + band_subfolder)
        os.rename(path['base'] + path['data'] + 'temp/' + filename_region,
                  path['base'] + path['data'] + band_subfolder + '/' + filename_region)
        os.remove(path['base'] + path['data'] + 'temp/' + filename)
        print('downloaded GOES-16 ABI {} B{:02d}, {:02d}.{:02d}.{:4d}, {:02d}:{:02d}UTC'.format(
               product_fullname, band, date.day, date.month, date.year, date.hour, date.minute))
        return filename_region

    elif product == 'L2-CMIPM':
        band_subfolder = 'b{:02d}'.format(band)
        if not band_subfolder in os.listdir(path['base'] + path['data']):
            os.mkdir(path['base'] + path['data'] + band_subfolder)
        os.rename(path['base'] + path['data'] + 'temp/' + filename,
                  path['base'] + path['data'] + band_subfolder + '/' + filename)
        print('downloaded GOES-16 ABI {} B{:02d}, {:02d}.{:02d}.{:02d}, {:02d}:{:02d}UTC'.format(
               product_fullname, band, date.day, date.month, date.year, date.hour, date.minute))
        return filename

############################################################################
############################################################################
############################################################################

def cut_file_to_region(path, filename_full, band, region):

    filename_region = filename_full[:-3] + '_region-' + region + '.nc'
    dataset_full = xr.open_dataset(path['base'] + path['data'] + 'temp/' + filename_full)


    # base resolution is 2km at nadir, bands 1,3,5 have 1km resolution at nadir and band 2 is 0.5km at nadir #

    if band == 1 \
     or band == 3 \
     or band == 5:
        f_res = 2
    elif band == 2:
        f_res = 4
    else:
        f_res = 1


    # add new regions here #

    if region == 'fulldisk':
        y_min = 0
        y_max = 5424
        x_min = 0
        x_max = 5424
    elif region == 'ssa':
        y_min = 3300
        y_max = 5200
        x_min = 2500
        x_max = 4200
    elif region == 'atacama':
        y_min = 3400
        y_max = 4400
        x_min = 2550
        x_max = 3100
    elif region == 'atacama_squared':
        y_min = 3400
        y_max = 4400
        x_min = 2350
        x_max = 3450


    # crop arrays to region boundaries #

    dataset_region = dataset_full.copy(deep = True)
    dataset_region = dataset_region.drop_dims(['x', 'y'])
    dataset_region['x'] = dataset_full['x'][x_min * f_res : x_max * f_res]
    dataset_region['y'] = dataset_full['y'][y_min * f_res : y_max * f_res]
    dataset_region['CMI'] = dataset_full['CMI'][y_min * f_res : y_max * f_res, x_min * f_res : x_max * f_res]
    dataset_region['DQF'] = dataset_full['DQF'][y_min * f_res : y_max * f_res, x_min * f_res : x_max * f_res]
    dataset_region['x'].attrs['_FillValue'] = -1    # full disk variable range is -0.151844 to 0.151844
    dataset_region['y'].attrs['_FillValue'] = -1    # full disk variable range is -0.151844 to 0.151844
    dataset_region.to_netcdf(path['base'] + path['data'] + 'temp/' + filename_region)

    dataset_region.close()
    dataset_full.close()


    return filename_region

############################################################################
############################################################################
############################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    delta_t = t2-t1
    if delta_t < 60:
        print('total script time:  {:.1f}s'.format(delta_t))
    elif 60 <= delta_t <= 3600:
        print('total script time:  {:.0f}min{:.0f}s'.format(delta_t//60, delta_t-delta_t//60*60))
    else:
        print('total script time:  {:.0f}h{:.0f}min'.format(delta_t//3600, (delta_t-delta_t//3600*3600)/60))
