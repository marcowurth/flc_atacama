
########################################################################################################################
###                                                                                                                  ###
###  This module uses a width of max. 120 characters                                                                 ###
###                                                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: numpy                                                                             ###
###                                                                                                                  ###
###  Content:                                                                                                        ###
###   The functions in this module do different image algorithms                                                     ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   This module here containes functions that have to be imported by another function or script                    ###
###                                                                                                                  ###
########################################################################################################################

import numpy as np


def enhance_b02_max_contrast_algorithm(image_array_b02_coldmasked, sza_b02):

    # max contrast algorithm for GOES Band 2 cloud tops in severe storms to be used in VIS-IR sandwich images
    # algorithm from Marco Wurth, Dec 2020
    # developed from subjectively fitting gamma, range_min, range_max to the whole range of solar zenith angles,
    # fitted quadratic polynomials to cos(sza) and gamma

    sza_cos = np.cos(np.deg2rad(sza_b02))
    gamma_poly_values = [1.9, -3.3, 1.6]
    range_min_poly_values = [0.02, -0.008, 0.03]
    range_max_poly_values = [1.3, -1.7, 0.9] # quadratic for gamma=0.2 to 1.0; constant 0.5 for higher gamma

    gamma = gamma_poly_values[2] * sza_cos * sza_cos + gamma_poly_values[1] * sza_cos + gamma_poly_values[0]
    range_min = range_min_poly_values[2] * gamma * gamma + range_min_poly_values[1] * gamma + range_min_poly_values[0]
    range_max = np.where(gamma > 1.0, 0.5,
                range_max_poly_values[2] * gamma * gamma + range_max_poly_values[1] * gamma + range_max_poly_values[0])

    image_array_b02_coldmasked_enh = (image_array_b02_coldmasked ** (1 / gamma) - range_min) / (range_max - range_min)

    return image_array_b02_coldmasked_enh



def enhance_vis_piecewise_linear(image_array):

    # algorithm from Jacques Descloitres, NASA/GSFC (Liam Gumley et al. 2010)
    # uses piece-wise linear stretching

    image_array_enh = np.zeros_like(image_array, dtype='float64')
    image_array = np.where(image_array < 0.0, 0.0, image_array)
    image_array = np.where(image_array > 1.0, 1.0, image_array)

    input_thresholds  = np.array([0,  30,  60, 120, 190, 255], dtype='float64') / 255
    output_thresholds = np.array([0, 110, 160, 210, 240, 255], dtype='float64') / 255

    boundary_thresh = 0.00001   # threshold diff for values that are zero or one

    for i in range(input_thresholds.shape[0] - 1):
        filter_image = np.where(image_array < input_thresholds[i] + boundary_thresh,
                                np.ones_like(image_array),
                                np.where(image_array > input_thresholds[i+1] - boundary_thresh,
                                         np.ones_like(image_array),
                                         np.zeros_like(image_array)))
        image_array_enh = np.where(filter_image,
                                       image_array_enh,
                                       (image_array - input_thresholds[i]) \
                                        / (input_thresholds[i+1] - input_thresholds[i])\
                                        * (output_thresholds[i+1] - output_thresholds[i])\
                                        + output_thresholds[i] )
    image_array_enh = np.where(image_array < 0.0 + boundary_thresh, 0.0, image_array_enh)
    image_array_enh = np.where(image_array > 1.0 - boundary_thresh, 1.0, image_array_enh)

    return image_array_enh
