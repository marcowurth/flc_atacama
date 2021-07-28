
########################################################################################################################
###                                                                                                                  ###
###  This module uses a width of max. 120 characters                                                                 ###
###                                                                                                                  ###
###  Author: Marco Wurth, July 2021                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: None                                                                              ###
###                                                                                                                  ###
###  Content:                                                                                                        ###
###   The function in this module returns an information string depending on type and band number                    ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   This module here containes functions that have to be imported by another function or script                    ###
###                                                                                                                  ###
########################################################################################################################

def get_band_info(band_num, info_type):

    if info_type == 'resolution_nadir':
        if band_num == 1:
            info = 1.0
        if band_num == 2:
            info = 0.5
        if band_num == 3:
            info = 1.0
        if band_num == 4:
            info = 2.0
        if band_num == 5:
            info = 1.0
        if band_num == 6:
            info = 1.0
        if band_num == 7:
            info = 2.0
        if band_num == 8:
            info = 2.0
        if band_num == 9:
            info = 2.0
        if band_num == 10:
            info = 2.0
        if band_num == 11:
            info = 2.0
        if band_num == 12:
            info = 2.0
        if band_num == 13:
            info = 2.0
        if band_num == 14:
            info = 2.0
        if band_num == 15:
            info = 2.0
        if band_num == 16:
            info = 2.0


    elif info_type == 'central_wavelength':
        if band_num == 1:
            info = '0.47µm'
        if band_num == 2:
            info = '0.64µm'
        if band_num == 3:
            info = '0.86µm'
        if band_num == 4:
            info = '1.38µm'
        if band_num == 5:
            info = '1.61µm'
        if band_num == 6:
            info = '2.25µm'
        if band_num == 7:
            info = '3.9µm'
        if band_num == 8:
            info = '6.2µm'
        if band_num == 9:
            info = '6.9µm'
        if band_num == 10:
            info = '7.3µm'
        if band_num == 11:
            info = '8.5µm'
        if band_num == 12:
            info = '9.6µm'
        if band_num == 13:
            info = '10.3µm'
        if band_num == 14:
            info = '11.2µm'
        if band_num == 15:
            info = '12.3µm'
        if band_num == 16:
            info = '13.3µm'

    elif info_type == 'abbreviation':
        if band_num == 1:
            info = 'VIS'
        if band_num == 2:
            info = 'VIS'
        if band_num == 3:
            info = 'NIR'
        if band_num == 4:
            info = 'SWIR'
        if band_num == 5:
            info = 'SWIR'
        if band_num == 6:
            info = 'SWIR'
        if band_num == 7:
            info = 'MWIR'
        if band_num == 8:
            info = 'MWIR'
        if band_num == 9:
            info = 'MWIR'
        if band_num == 10:
            info = 'MWIR'
        if band_num == 11:
            info = 'LWIR'
        if band_num == 12:
            info = 'LWIR'
        if band_num == 13:
            info = 'LWIR'
        if band_num == 14:
            info = 'LWIR'
        if band_num == 15:
            info = 'LWIR'
        if band_num == 16:
            info = 'LWIR'

    return info
