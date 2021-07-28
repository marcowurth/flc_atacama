
########################################################################################################################
###                                                                                                                  ###
###  This module uses a width of max. 120 characters                                                                 ###
###                                                                                                                  ###
###  Author: Marco Wurth, July 2021                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: None                                                                              ###
###                                                                                                                  ###
###  Content:                                                                                                        ###
###   This module containes several calculation functions                                                            ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   This module here containes functions that have to be imported by another function or script                    ###
###                                                                                                                  ###
########################################################################################################################

from general.calc_solar_zenith_angle import calc_sza
from general.image_enhancement_algorithms import enhance_vis_piecewise_linear, enhance_b02_max_contrast_algorithm

########################################################################################################################
#  This function calculates reflectance or brightness temperature depending on abi band number                         #
########################################################################################################################

def calculate_rv_or_bt(
        band, normalization, date_sensed, lons, lats, image_array):

    if band <= 6:

        # apply for bands with reflectance values #

        sza = calc_sza(date_sensed, lons, lats)

        if normalization == 'none':
            #percentile = 0.1
            #print('reflectance: perc-{:.1f}%: {:.3f} perc-{:.1f}%: {:.2f}'.format(
            #      percentile, np.nanpercentile(image_array, percentile),
            #      100 - percentile, np.nanpercentile(image_array, 100 - percentile)))
            pass
        elif normalization == 'piecewise_linear':
            image_array = enhance_vis_piecewise_linear(image_array)
        elif normalization == 'max_storm_contrast':
            image_array = enhance_b02_max_contrast_algorithm(image_array, sza)
    else:

        # convert IR BT data from Kelvin to degC #

        image_array -= 273.15
        #print('min BT: {:.1f} °C'.format(np.nanmin(image_array)))

    return image_array

########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################

########################################################################################################################
#  This two functions calculate band difference or ndvi                                                                #
########################################################################################################################

def calculate_band_difference(image_array_A, image_array_B):
    image_array =  image_array_A - image_array_B
    return image_array

def calculate_ndvi(image_array_A, image_array_B):
    image_array =  (image_array_B - image_array_A) / (image_array_B + image_array_A)
    return image_array


