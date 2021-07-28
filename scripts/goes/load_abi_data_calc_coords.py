
########################################################################################################################
###                                                                                                                  ###
###  This module uses a width of max. 120 characters                                                                 ###
###                                                                                                                  ###
###  Author: Marco Wurth, July 2021                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: numpy, xarray, netcdf4, pyproj, xesmf                                             ###
###                                                                                                                  ###
###  Content:                                                                                                        ###
###   This module is for ABI's L2-CMIP file reading, geolocation calculation, domain cropping and downsampling       ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   This module here containes functions that have to be imported by another function or script                    ###
###                                                                                                                  ###
########################################################################################################################

import os
import datetime
import fnmatch

import numpy as np
import xarray as xr
import pyproj
import xesmf

from general.domain_definitions import get_image_domain
from general.crop_data import crop_data

########################################################################################################################
#  This function loads data from a single band and timestep, calculates its geolocation and performs domain cropping   #
#  and downsampling                                                                                                    #
########################################################################################################################

def load_data_single_band(
        base_path, product_fullname, region, mode, band,
        date_data_file, sensing_timedelta,
        domain_name, downsampling_factor):

    # divide product_fullname string into product only and mesoscale sector number #

    if product_fullname == 'L2-CMIPF':
        product = product_fullname
    elif product_fullname[:-1] == 'L2-CMIPM':
        product = product_fullname[:-1]
        meso_num = int(product_fullname[-1])


    # set all paths required in this function #

    path = dict(base = base_path,
                data = 'data/ABI/GOES-16/{}/'.format(product),
                image = 'images/GOES-16/single_band/b{:02d}/'.format(band),
                colorpalette = 'data/additional_data/colorpalettes/')


    # apply sensing timedelta #

    if product == 'L2-CMIPF':
        date_sensed = date_data_file + datetime.timedelta(minutes = sensing_timedelta)
    elif product == 'L2-CMIPM':
        date_sensed = date_data_file


    # search and open goes-16 file #

    dayofyear = (date_data_file - datetime.datetime(date_data_file.year, 1, 1)).days + 1
    match_string = '*{}-M6C{:02d}_G16_s{:4d}{:03d}{:02d}{:02d}*region-{}.nc'.format(
                    product_fullname, band,
                    date_data_file.year, dayofyear, date_data_file.hour, date_data_file.minute,
                    region)
    files_list = os.listdir(path['base'] + path['data'] + 'b{:02d}/'.format(band))

    filename = None
    for file in files_list:
        if fnmatch.fnmatch(file, match_string):
            filename = file
    if filename == None:
        print('----- abi file not found -----')
        print('----- match_string: {} -----'.format(match_string))
        print('----- path: {} -----'.format(path['base'] + path['data'] + 'b{:02d}/'.format(band)))
        return

    goes_dataset = xr.open_dataset(path['base'] + path['data'] + 'b{:02d}/'.format(band) + filename)
    image_array = goes_dataset['CMI'].values


    # set offset to the ABI file geolocation in metres #

    x_offset = 0
    y_offset = 0


    # calculate geographical coordinates of the data file coordinates #

    x = goes_dataset['x'].values + x_offset
    y = goes_dataset['y'].values + y_offset

    sat = dict(goes_number = 16)
    sat['h'] = goes_dataset['goes_imager_projection'].perspective_point_height
    sat['lon'] = goes_dataset['goes_imager_projection'].longitude_of_projection_origin
    sat['sweep'] = goes_dataset['goes_imager_projection'].sweep_angle_axis

    p = pyproj.Proj(proj = 'geos', h = sat['h'], lon_0 = sat['lon'], sweep = sat['sweep'], ellps = 'GRS80')
    xx, yy = np.meshgrid(x * sat['h'], y * sat['h'])
    lons, lats = p(xx, yy, inverse = True)

    lats = np.ma.masked_outside(lats, -90.0, 90.0)
    lons = np.ma.masked_outside(lons, -180.0, 180.0)
    lats.fill_value = 1000
    lons.fill_value = 1000

    del x, y, p, xx, yy
    goes_dataset.close()


    # crop data to plotting domain #
    # the cropping margin is dynamical and 20% degrees of the plot domain radius #

    domain = get_image_domain(domain_name)

    if product == 'L2-CMIPF' and domain['name'] != 'GOES-East_fulldisk':
        try:
            margin_deg = 0.2 * domain['radius'] / 111
            index_x_first, index_x_last, index_y_first, index_y_last = crop_data(image_array, lats, lons, domain,
                                                                                 margin_deg, False)
            image_array = image_array[index_y_first:index_y_last+1, index_x_first:index_x_last+1]
            lats = lats[index_y_first:index_y_last+1, index_x_first:index_x_last+1]
            lons = lons[index_y_first:index_y_last+1, index_x_first:index_x_last+1]
        except np.AxisError:
            pass


    # do effective nearest neighbor regridding if set on #

    if downsampling_factor > 1:
        image_array = image_array[::downsampling_factor, ::downsampling_factor]
        lats = lats[::downsampling_factor, ::downsampling_factor]
        lons = lons[::downsampling_factor, ::downsampling_factor]
        downsampling_str = '_NNx{:d}'.format(downsampling_factor)
    else:
        downsampling_str = ''


    lats = lats.filled()
    lons = lons.filled()


    return date_sensed, path, sat, domain, downsampling_str, lons, lats, image_array

########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################

########################################################################################################################
#  This function loads data from two bands but one timestep, calculates its geolocation and performs upsampling of the #
#  lower resolution band, does domain cropping and downsampling and then returns the bands data on the same grid       #
########################################################################################################################

def load_data_band_combination(
        base_path, product_fullname, region, mode, band_combination,
        date_data_file, sensing_timedelta,
        domain_name, downsampling_factor):

    # divide product_fullname string into product only and mesoscale sector number #

    if product_fullname == 'L2-CMIPF':
        product = product_fullname
    elif product_fullname[:-1] == 'L2-CMIPM':
        product = product_fullname[:-1]
        meso_num = int(product_fullname[-1])


    # set all paths required in this function #

    path = dict(base = base_path,
                data = 'data/ABI/GOES-16/{}/'.format(product),
                image = 'images/GOES-16/',
                colorpalette = 'data/additional_data/colorpalettes/')

    if mode == 'band_difference':
        path['image'] += 'band_difference/b{:02d}-b{:02d}/'.format(band_combination[0], band_combination[1])
    elif mode == 'ndvi':
        path['image'] += 'ndvi/'


    # apply sensing timedelta #

    if product == 'L2-CMIPF':
        date_sensed = date_data_file + datetime.timedelta(minutes = sensing_timedelta)
    elif product == 'L2-CMIPM':
        date_sensed = date_data_file

    if get_band_info(band_combination[0], 'resolution_nadir') == get_band_info(band_combination[1], 'resolution_nadir'):
        coordinates_are_equal = True
    else:
        coordinates_are_equal = False


    # search and open goes-16 file A #

    dayofyear = (date_data_file - datetime.datetime(date_data_file.year, 1, 1)).days + 1
    match_string = '*{}-M6C{:02d}_G16_s{:4d}{:03d}{:02d}{:02d}*region-{}.nc'.format(
                    product_fullname, band_combination[0],
                    date_data_file.year, dayofyear, date_data_file.hour, date_data_file.minute,
                    region)
    files_list = os.listdir(path['base'] + path['data'] + 'b{:02d}/'.format(band_combination[0]))

    filename = None
    for file in files_list:
        if fnmatch.fnmatch(file, match_string):
            filename = file
    if filename == None:
        print('----- abi file not found -----')
        print('----- match_string: {} -----'.format(match_string))
        print('----- path: {} -----'.format(path['base'] + path['data'] + 'b{:02d}/'.format(band_combination[0])))
        return

    goes_dataset = xr.open_dataset(path['base'] + path['data'] + 'b{:02d}/'.format(band_combination[0]) + filename)
    image_array_A = goes_dataset['CMI'].values


    # set offset to the ABI file geolocation in metres #

    x_offset = 0
    y_offset = 0


    # calculate geographical coordinates of the data file coordinates #

    x = goes_dataset['x'].values + x_offset
    y = goes_dataset['y'].values + y_offset

    sat = dict(goes_number = 16)
    sat['h'] = goes_dataset['goes_imager_projection'].perspective_point_height
    sat['lon'] = goes_dataset['goes_imager_projection'].longitude_of_projection_origin
    sat['sweep'] = goes_dataset['goes_imager_projection'].sweep_angle_axis

    p = pyproj.Proj(proj = 'geos', h = sat['h'], lon_0 = sat['lon'], sweep = sat['sweep'], ellps = 'GRS80')
    xx, yy = np.meshgrid(x * sat['h'], y * sat['h'])
    lons_A, lats_A = p(xx, yy, inverse = True)

    lats_A = np.ma.masked_outside(lats_A, -90.0, 90.0)
    lons_A = np.ma.masked_outside(lons_A, -180.0, 180.0)
    lats_A.fill_value = np.nan
    lons_A.fill_value = np.nan
    #lats_A = lats_A.filled()
    #lons_A = lons_A.filled()

    del x, y, p, xx, yy
    goes_dataset.close()


    # search and open goes-16 file B #

    dayofyear = (date_data_file - datetime.datetime(date_data_file.year, 1, 1)).days + 1
    match_string = '*{}-M6C{:02d}_G16_s{:4d}{:03d}{:02d}{:02d}*region-{}.nc'.format(
                    product_fullname, band_combination[1],
                    date_data_file.year, dayofyear, date_data_file.hour, date_data_file.minute,
                    region)
    files_list = os.listdir(path['base'] + path['data'] + 'b{:02d}/'.format(band_combination[1]))

    filename = None
    for file in files_list:
        if fnmatch.fnmatch(file, match_string):
            filename = file
    if filename == None:
        print('----- abi file not found -----')
        print('----- match_string: {} -----'.format(match_string))
        print('----- path: {} -----'.format(path['base'] + path['data'] + 'b{:02d}/'.format(band_combination[1])))
        return

    goes_dataset = xr.open_dataset(path['base'] + path['data'] + 'b{:02d}/'.format(band_combination[1]) + filename)
    image_array_B = goes_dataset['CMI'].values

    if not coordinates_are_equal:

        # set offset to the ABI file geolocation in metres #

        x_offset = 0
        y_offset = 0


        # calculate geographical coordinates of the data file coordinates #

        x = goes_dataset['x'].values + x_offset
        y = goes_dataset['y'].values + y_offset

        sat = dict(goes_number = 16)
        sat['h'] = goes_dataset['goes_imager_projection'].perspective_point_height
        sat['lon'] = goes_dataset['goes_imager_projection'].longitude_of_projection_origin
        sat['sweep'] = goes_dataset['goes_imager_projection'].sweep_angle_axis

        p = pyproj.Proj(proj = 'geos', h = sat['h'], lon_0 = sat['lon'], sweep = sat['sweep'], ellps = 'GRS80')
        xx, yy = np.meshgrid(x * sat['h'], y * sat['h'])
        lons_B, lats_B = p(xx, yy, inverse = True)

        lats_B = np.ma.masked_outside(lats_B, -90.0, 90.0)
        lons_B = np.ma.masked_outside(lons_B, -180.0, 180.0)
        lats_B.fill_value = np.nan
        lons_B.fill_value = np.nan
        #lats_B = lats_B.filled()
        #lons_B = lons_B.filled()

        del x, y, p, xx, yy
    goes_dataset.close()


    # crop data to plotting domain #
    # the cropping margin is dynamical and 20% degrees of the plot domain radius #

    domain = get_image_domain(domain_name)

    if product == 'L2-CMIPF' and domain['name'] != 'GOES-East_fulldisk':
        try:
            margin_deg = 0.2 * domain['radius'] / 111
            index_x_first, index_x_last, index_y_first, index_y_last = crop_data(image_array_A, lats_A, lons_A,
                                                                                 domain, margin_deg, False)
            image_array_A = image_array_A[index_y_first:index_y_last+1, index_x_first:index_x_last+1]
            lats_A = lats_A[index_y_first:index_y_last+1, index_x_first:index_x_last+1]
            lons_A = lons_A[index_y_first:index_y_last+1, index_x_first:index_x_last+1]

            if coordinates_are_equal:
                image_array_B = image_array_B[index_y_first:index_y_last+1, index_x_first:index_x_last+1]
            else:
                index_x_first, index_x_last, index_y_first, index_y_last = crop_data(image_array_B, lats_B, lons_B,
                                                                                     domain, margin_deg, False)
                image_array_B = image_array_B[index_y_first:index_y_last+1, index_x_first:index_x_last+1]
                lats_B = lats_B[index_y_first:index_y_last+1, index_x_first:index_x_last+1]
                lons_B = lons_B[index_y_first:index_y_last+1, index_x_first:index_x_last+1]

        except np.AxisError:
            pass


    if coordinates_are_equal:
        lats = lats_A
        lons = lons_A
    else:
        print('resampling...')

        # do resampling from the coarser to the finer coordinates #

        # not yet working xarray method here #

        '''image_DataArray_A = xr.DataArray(data = image_array_A,
                                         dims = ('lat_index', 'lon_index'),
                                         coords = dict(lat_index = np.arange(lats_A.shape[0]),
                                                       lon_index = np.arange(lats_A.shape[1]),
                                                       lats = (('lat_index', 'lon_index'), lats_A),
                                                       lons = (('lat_index', 'lon_index'), lons_A)))
        image_DataArray_B = xr.DataArray(data = copy.deepcopy(image_array_B),
                                         dims = ('lat_index', 'lon_index'),
                                         coords = dict(lat_index = np.arange(lats_B.shape[0]),
                                                       lon_index = np.arange(lats_B.shape[1]),
                                                       lats = (('lat_index', 'lon_index'), lats_B),
                                                       lons = (('lat_index', 'lon_index'), lons_B)))

        if get_band_info(band_combination[0], 'resolution_nadir') \
         > get_band_info(band_combination[1], 'resolution_nadir'):
            image_array_A = image_DataArray_A.interp_like(image_DataArray_B).values
            lats = lats_B
            lons = lons_B
        else:
            image_array_B = image_DataArray_B.interp_like(image_DataArray_A).values
            lats = lats_A
            lons = lons_A'''


        # resampling with xesmf works but is quite slow for larger domains #

        if get_band_info(band_combination[0], 'resolution_nadir') \
         > get_band_info(band_combination[1], 'resolution_nadir'):
            regridder_1km_to_500m = xesmf.Regridder(dict(lat = np.ascontiguousarray(lats_A),
                                                         lon = np.ascontiguousarray(lons_A)),
                                                    dict(lat = np.ascontiguousarray(lats_B),
                                                         lon = np.ascontiguousarray(lons_B)),
                                                    'nearest_s2d')
            image_array_A = regridder_1km_to_500m(np.ascontiguousarray(image_array_A))
            lats = lats_B
            lons = lons_B
        else:
            regridder_1km_to_500m = xesmf.Regridder(dict(lat = np.ascontiguousarray(lats_B),
                                                         lon = np.ascontiguousarray(lons_B)),
                                                    dict(lat = np.ascontiguousarray(lats_A),
                                                         lon = np.ascontiguousarray(lons_A)),
                                                    'nearest_s2d')
            image_array_B = regridder_1km_to_500m(np.ascontiguousarray(image_array_B))
            lats = lats_A
            lons = lons_A


    # do effective nearest neighbor regridding if set on #

    if downsampling_factor > 1:
        image_array_A = image_array_A[::downsampling_factor, ::downsampling_factor]
        image_array_B = image_array_B[::downsampling_factor, ::downsampling_factor]
        lats = lats[::downsampling_factor, ::downsampling_factor]
        lons = lons[::downsampling_factor, ::downsampling_factor]

        downsampling_str = '_NNx{:d}'.format(downsampling_factor)
    else:
        downsampling_str = ''


    lats = lats.filled()
    lons = lons.filled()


    return date_sensed, path, sat, domain, downsampling_str, \
           lons, lats, image_array_A, image_array_B
