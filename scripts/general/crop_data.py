
########################################################################################################################
###                                                                                                                  ###
###  This module uses a width of max. 120 characters                                                                 ###
###                                                                                                                  ###
###  Author: Marco Wurth, July 2021                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: numpy                                                                             ###
###                                                                                                                  ###
###  Content:                                                                                                        ###
###   The function in this module calculates the indices of the array boundaries depending on a domain and margin    ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   This module here containes functions that have to be imported by another function or script                    ###
###                                                                                                                  ###
########################################################################################################################

import numpy as np


def crop_data(image_data, lats, lons, domain, margin_deg, verbose):

    if verbose:
        print('image_data:', image_data.shape)
        print('lats:', lats.shape)
        print('lons:', lons.shape)
        print('----- mask out-of-domain pixels... -----')

    cutout = dict()
    if domain['limits_type'] == 'radius':
        cutout['lat_min'] = float(np.where(domain['centerlat'] - domain['radius'] / 111.2 - margin_deg < -90, -90,
                                  domain['centerlat'] - domain['radius'] / 111.2 - margin_deg))
        cutout['lat_max'] = float(np.where(domain['centerlat'] + domain['radius'] / 111.2 + margin_deg > 90, 90,
                                  domain['centerlat'] + domain['radius'] / 111.2 + margin_deg))
        cutout['lon_min'] = float(np.where(cutout['lat_min'] <= -90 or cutout['lat_max'] >= 90, -180.1,
                                  domain['centerlon'] - domain['radius'] \
                                  / (111.2 * np.cos(domain['centerlat']*np.pi/180)) - margin_deg))
        cutout['lon_max'] = float(np.where(cutout['lat_min'] <= -90 or cutout['lat_max'] >= 90, 180,
                                  domain['centerlon'] + domain['radius'] \
                                  / (111.2 * np.cos(domain['centerlat']*np.pi/180)) + margin_deg))
    else:
        print('domain limits_type {} not supported yet!'.format(domain['limits_type']))
        exit()

    lats = np.ma.masked_outside(lats, cutout['lat_min'], cutout['lat_max'])
    lons = np.ma.masked_outside(lons, cutout['lon_min'], cutout['lon_max'])


    # combine all three masks #

    image_data = np.ma.masked_where(lats.mask==True, image_data)
    image_data = np.ma.masked_where(lons.mask==True, image_data)
    lats = np.ma.masked_where(image_data.mask==True, lats)
    lons = np.ma.masked_where(image_data.mask==True, lons)

    #print_masked_array_stats(image_data, 'image_data')

    num_values_before = image_data.shape[0] * image_data.shape[1]


    # reduce arrays to smallest possible #

    x_mask = np.ma.all(image_data.mask,0)
    y_mask = np.ma.all(image_data.mask,1)

    index_x_first = np.where(x_mask==False)[0][0]
    index_x_last = np.where(x_mask==False)[0][-1]
    index_y_first = np.where(y_mask==False)[0][0]
    index_y_last = np.where(y_mask==False)[0][-1]

    if verbose:
        print('x subset:', index_x_first, index_x_last)
        print('y subset:', index_y_first, index_y_last)

        image_data = image_data[index_y_first:index_y_last+1, index_x_first:index_x_last+1]
        lats = lats[index_y_first:index_y_last+1, index_x_first:index_x_last+1]
        lons = lons[index_y_first:index_y_last+1, index_x_first:index_x_last+1]

        num_values_after = image_data.shape[0] * image_data.shape[1]

        print('----- reduced arrays to {:.2f}%... -----'.format(\
                100. * num_values_after / num_values_before))

        #print_masked_array_stats(image_data, 'image_data')

        print('image_data:', image_data.shape)
        print('lats:', lats.shape)
        print('lons:', lons.shape)

    return index_x_first, index_x_last, index_y_first, index_y_last
