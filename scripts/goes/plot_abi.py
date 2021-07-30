
########################################################################################################################
###                                                                                                                  ###
###  This script uses a width of max. 120 characters                                                                 ###
###                                                                                                                  ###
###  Author: Marco Wurth, July 2021                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: None                                                                              ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   1) Execute in terminal folder>python plot_abi.py                                                               ###
###   2) Via import of plot_abi from another script                                                                  ###
###                                                                                                                  ###
########################################################################################################################

import sys
import datetime

base_path = ''
sys.path.append(base_path + 'scripts')

from goes.load_abi_data_calc_coords import load_data_single_band, load_data_band_combination
from goes.calc_image import calculate_rv_or_bt, calculate_band_difference, calculate_ndvi
from goes.plot_image import plot_image


def plot_abi():

    # set product and region of data file, region is ignored for mesoscale sector files #

    product = 'L2-CMIPF'
    #product = 'L2-CMIPM1'
    #product = 'L2-CMIPM2'

    #region = 'fulldisk'
    #region = 'ssa'
    region = 'atacama'
    #region = 'atacama_squared'


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


    # set plot mode #

    mode = 'single_band'
    #mode = 'band_difference'
    #mode = 'ndvi'
    #mode = 'composite'
    #mode = 'SSIM'
    #mode = 'product_classification'
    #mode = 'product_statistics'


    # set bands combinations #

    # single_band mode: list of numbers, possible 1-16 #
    bands = [7, 13]
    #bands = list(range(1, 6+1))

    # band_difference mode: list of tuples of numbers, (13, 7) means B13-B07 will be plotted #
    #band_combinations = [(13, 7), (15, 11)]
    #band_combinations = [(15, 11)]

    # ndvi mode: bands settings ignored #
    #band_combination = (2, 3)


    # set domain and plot projection type #

    domain_names = []
    #domain_names.append('Atacama_Peru_West')
    #domain_names.append('Atacama_Peru_East')
    #domain_names.append('Atacama_Chile_North')
    #domain_names.append('Atacama_Chile_Central')
    #domain_names.append('Atacama_Chile_South')
    #domain_names.append('Atacama_Squared')
    domain_names.append('GOES-East_fulldisk')

    projection = 'orthographic'
    #projection = 'geostationary'


    # set timedelta between data file initial time and sensing time #
    #  full disk scanning of the ABI begins at the North Pole and goes in zonal stripes southward until after 10min #
    #  reaching the South Pole #

    sensing_timedelta = 7


    # set the resolution (total width) of plot + colorbar #
    #  because matplotlib make only square maps the top & bottom whitespace will be cropped after plotting #
    #  this results in a height smaller than this value #

    resolution = 1000


    # set downsampling factor (via nearest neighbor regridding), 1 means downsampling is skipped #

    #downsampling_factor = 1
    downsampling_factor = 4


    # set data normalization method, only applied if vis single-band used #

    normalization = 'none'
    #normalization = 'piecewise_linear'
    #normalization = 'max_storm_contrast'


    # set colorbar #

    #colorpalette = 'Gray_BW'
    colorpalette = 'Classic-IR'    # this one overrides all cmap range settings set below 
    #colorpalette = 'viridis'
    #colorpalette = 'plasma'
    #colorpalette = 'inferno'
    #colorpalette = 'magma'
    #colorpalette = 'cividis'
    #colorpalette = 'Hawaii'
    #colorpalette = 'LaJolla'
    #colorpalette = 'LaPaz'
    #colorpalette = 'Oslo'
    #colorpalette = 'Bilbao'
    #colorpalette = 'Roma'
    #colorpalette = 'LaJolla+Oslo'
    #colorpalette = 'Oslo+LaJolla'
    #colorpalette = 'LaJolla+Devon'

    cmap_reversed = False
    #cmap_reversed = True

    #cmap_range_max = 5
    #cmap_range_min = -5
    cmap_range_max = 1
    cmap_range_min = 0

    cmap_num_colors_between = 100


    # set border and missing value color, gridlines on/off #

    missing_value_color = 'white'
    #missing_value_color = 'magenta'

    border_color = 'white'
    #border_color = 'black'

    #gridlines_on = False
    gridlines_on = True


    # set render type, for interactive the default is rendering in browser #

    render_type = 'png'
    #render_type = 'interactive'


    # serial execution #

    for day in days:
        for hour in hours:
            for minute in minutes:

                if mode == 'single_band':
                    for band in bands:
                        for domain_name in domain_names:
                            date_data_file = datetime.datetime(year, month, day, hour, minute)
                            print('plot:'.ljust(8), date_data_file, 'band:', band, 'domain:', domain_name)

                            date_sensed, path, sat, domain, downsampling_str, lons, lats, image_array \
                             = load_data_single_band(
                                   base_path, product, region, mode, band,
                                   date_data_file, sensing_timedelta,
                                   domain_name, downsampling_factor)

                            image_array = calculate_rv_or_bt(
                                band, normalization, date_sensed, lons, lats, image_array)

                            plot_image(
                                   path, mode, band, date_sensed, sat, lons, lats, image_array,
                                   domain, projection, resolution, downsampling_str, normalization,
                                   colorpalette, cmap_reversed, cmap_range_min, cmap_range_max, cmap_num_colors_between,
                                   missing_value_color, border_color, gridlines_on, render_type)

                elif mode == 'band_difference':
                    for band_combination in band_combinations:
                        for domain_name in domain_names:
                            date_data_file = datetime.datetime(year, month, day, hour, minute)
                            print('plot:'.ljust(8), date_data_file, 'band_combination', band_combination, 'domain:', domain_name)

                            date_sensed, path, sat, domain, downsampling_str, \
                            lons, lats, image_array_A, image_array_B \
                             = load_data_band_combination(
                                   base_path, product, region, mode, band_combination,
                                   date_data_file, sensing_timedelta,
                                   domain_name, downsampling_factor)

                            image_array = calculate_band_difference(image_array_A, image_array_B)

                            plot_image(
                                   path, mode, band_combination, date_sensed, sat, lons, lats, image_array,
                                   domain, projection, resolution, downsampling_str, normalization,
                                   colorpalette, cmap_reversed, cmap_range_min, cmap_range_max, cmap_num_colors_between,
                                   missing_value_color, border_color, gridlines_on, render_type)

                elif mode == 'ndvi':
                    for domain_name in domain_names:
                        date_data_file = datetime.datetime(year, month, day, hour, minute)
                        print('plot:'.ljust(8), date_data_file, 'ndvi', 'domain:', domain_name)

                        date_sensed, path, sat, domain, downsampling_str, \
                        lons, lats, image_array_A, image_array_B \
                         = load_data_band_combination(
                               base_path, product, region, mode, band_combination,
                               date_data_file, sensing_timedelta,
                               domain_name, downsampling_factor)

                        image_array = calculate_ndvi(image_array_A, image_array_B)

                        plot_image(
                               path, mode, band_combination, date_sensed, sat, lons, lats, image_array,
                               domain, projection, resolution, downsampling_str, normalization,
                               colorpalette, cmap_reversed, cmap_range_min, cmap_range_max, cmap_num_colors_between,
                               missing_value_color, border_color, gridlines_on, render_type)

    return

############################################################################
############################################################################
############################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    plot_abi()
    t2 = time.time()
    delta_t = t2-t1
    if delta_t < 60:
        print('total script time:  {:.1f}s'.format(delta_t))
    elif 60 <= delta_t <= 3600:
        print('total script time:  {:.0f}min{:.0f}s'.format(delta_t//60, delta_t-delta_t//60*60))
    else:
        print('total script time:  {:.0f}h{:.0f}min'.format(delta_t//3600, (delta_t-delta_t//3600*3600)/60))
