
########################################################################################################################
###                                                                                                                  ###
###  This module uses a width of max. 120 characters                                                                 ###
###                                                                                                                  ###
###  Author: Marco Wurth, July 2021                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: numpy, cartopy, matplotlib, pillow                                                ###
###                                                                                                                  ###
###  Content:                                                                                                        ###
###   The function in this module draws the image on a map with a certain domain and all its settings                ###
###   Should mainly work for all geolocated images but the image name and description string are written for ABI     ###
###    images specifically, so for other images these two parts have to be complemented                              ###
###   If a static png image is made, its width equals the set resolution but its height <= resolution                ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   This module here containes functions that have to be imported by another function or script                    ###
###                                                                                                                  ###
########################################################################################################################

import os
import warnings

import numpy as np
import cartopy
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from PIL import Image

from general.make_my_colormap import generate_cmap
from goes.abi_information import get_band_info

########################################################################################################################
#  Plotting part                                                                                                       #
########################################################################################################################

def plot_image(
        path, mode, band, date_sensed, sat, lons, lats, image_array,
        domain, projection, resolution, downsampling_str, normalization,
        colorpalette, cmap_reversed, cmap_range_min, cmap_range_max, cmap_num_colors_between,
        missing_value_color, border_color, gridlines_on, render_type):


    # generate cmap and clevels #

    cmap, clevels, cmap_str = generate_cmap(path, colorpalette, cmap_reversed, missing_value_color,
                                            cmap_num_colors_between, cmap_range_min, cmap_range_max)

    if colorpalette == 'Classic-IR':
        cmap_cbar, clevels_cbar = generate_cmap(path, colorpalette, cmap_reversed, missing_value_color,
                                                cmap_num_colors_between, cmap_range_min, cmap_range_max,
                                                lowres_classic_ir_cbar = True)


    # create subfolder if necessary #

    if mode == 'single_band':
        if not path['image'][-4:-1] in os.listdir(path['base'] + path['image'][:-4]):
            os.mkdir(path['base'] + path['image'][:-1])
    elif mode == 'band_difference':
        if not path['image'][-8:-1] in os.listdir(path['base'] + path['image'][:-8]):
            os.mkdir(path['base'] + path['image'][:-1])


    # set filename of the resulting image #

    if mode == 'single_band':
        if band <= 2:
            plotname = 'Band_{:02d}_VIS_Norm-{}'.format(band, normalization)
        elif band == 3:
            plotname = 'Band_{:02d}_NIR_Norm-{}'.format(band, normalization)
        elif band >= 4 and band <= 6:
            plotname = 'Band_{:02d}_SWIR_Norm-{}'.format(band, normalization)
        elif (band >= 7) and (band <= 10):
            plotname = 'Band_{:02d}_MWIR'.format(band)
        elif band >= 11 and band <= 16:
            plotname = 'Band_{:02d}_LWIR'.format(band)
    elif mode == 'band_difference':
        plotname = 'Band_B{:02d}-B{:02d}'.format(band[0], band[1])
    elif mode == 'ndvi':
        plotname = 'NDVI'

    imagename = 'ABI_GOES-16_{}_{}_{}_{:4d}{:02d}{:02d}_{:02d}:{:02d}UTC_cmap-{}{}_{:d}px.png'.format(
                plotname, domain['name'], projection,
                date_sensed.year, date_sensed.month, date_sensed.day, date_sensed.hour, date_sensed.minute,
                cmap_str, downsampling_str, resolution)

    if render_type == 'png':
        print('plot {}...'.format(imagename))
    elif render_type == 'interactive':
        print('plot {} interactively...'.format(imagename[:-4]))


    # calculate domain limits #

    if domain['limits_type'] == 'radius':
        domain_limits = dict(
                             lat_min = float(np.where(domain['centerlat'] - domain['radius'] / 111.2 < -90,
                                                      -90, domain['centerlat'] - domain['radius'] / 111.2)),
                             lat_max = float(np.where(domain['centerlat'] + domain['radius'] / 111.2 > 90,
                                                       90, domain['centerlat'] + domain['radius'] / 111.2)),
                             )
        domain_limits['lon_min'] = float(np.where(domain_limits['lat_min'] <= -90 or domain_limits['lat_max'] >= 90,
                                       0,
                                       domain['centerlon'] - domain['radius'] \
                                        / (111.2 * np.cos(domain['centerlat']*np.pi/180))))
        domain_limits['lon_max'] = float(np.where(domain_limits['lat_min'] <= -90 or domain_limits['lat_max'] >= 90,
                                       360,
                                       domain['centerlon'] + domain['radius'] \
                                        / (111.2 * np.cos(domain['centerlat']*np.pi/180))))

        ext_regular = [domain_limits['lon_min'], domain_limits['lon_max'],
                       domain_limits['lat_min'], domain_limits['lat_max']]


    # create needed cartopy projections for the map and the pcolormesh() function #

    projection_regular = cartopy.crs.PlateCarree()

    if projection == 'orthographic':
        projection_plot = cartopy.crs.Orthographic(central_longitude = domain['centerlon'],
                                                   central_latitude = domain['centerlat'])
    elif projection == 'geostationary':
        projection_plot = cartopy.crs.Geostationary(central_longitude = sat['lon'], satellite_height = sat['h'],
                                                    sweep_axis = sat['sweep'])


    # set mpl backend and some line drawing speed optimizations #

    if render_type == 'png':
        mpl.use('AGG')

    elif render_type == 'interactive':
        mpl.use('webagg')   # should work system-independent in the browser
        #mpl.use('gtk3agg')
        #mpl.use('qt5agg')

    #mpl.style.use('fast')
    #mpl.rcParams['path.simplify_threshold'] = 1.0
    mpl.rcParams['agg.path.chunksize'] = 10000


    # create mpl figure and axes #

    subplotparameters = mpl.figure.SubplotParams(left = 0, bottom = 0, right = 0.91, top = 1, wspace = 0, hspace = 0)
    fig = plt.figure(figsize = (resolution / 100, resolution / 100), dpi = 100, subplotpars = subplotparameters)

    ax = plt.axes(projection = projection_plot)
    ax.set_extent(ext_regular, crs = projection_regular)


    # draw cartopy lines on map, cartopy should download the needed shapefile data automatically #

    ax.add_feature(cartopy.feature.STATES.with_scale('10m'), linewidth = 0.18, edgecolor = border_color)
    ax.add_feature(cartopy.feature.COASTLINE.with_scale('10m'), linewidth = 0.18, edgecolor = border_color)
    ax.add_feature(cartopy.feature.BORDERS.with_scale('10m'), linewidth = 0.18, edgecolor = border_color)
    #ax.add_feature(cartopy.feature.RIVERS.with_scale('110m'), linewidth = 0.5, edgecolor = 'blue')
    #ax.add_feature(cartopy.feature.LAKES.with_scale('110m'), linewidth = 0.5, edgecolor = 'blue',
    #                facecolor = (0, 0, 0, 0))


    # add grid lines #

    if gridlines_on:
        if domain['radius'] > 200:
            grid_spacing = 10.0
        elif domain['radius'] > 400:
            grid_spacing = 2.0
        else:
            grid_spacing = 1.0
        gl = ax.gridlines(crs = projection_regular, linewidth = 0.4, color = 'black')#,
        #                  draw_labels = True, x_inline = True, y_inline = True)
        gl.xlocator = mpl.ticker.FixedLocator(np.arange(-180, 180, grid_spacing))
        gl.ylocator = mpl.ticker.FixedLocator(np.arange(-90, 90+1, grid_spacing))


    # draw image on map with pcolormesh() #

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        norm = mpl.colors.BoundaryNorm(clevels, cmap.N)
        plotted_image = ax.pcolormesh(lons, lats, image_array,
                                      cmap = cmap, norm = norm, transform = projection_regular,
                                      antialiased = False)


    # draw colorbar legend #

    distance_plot_to_cbar = 0.01
    axins = inset_axes(ax, width = '3%', height = '100%', loc = 'lower left',
                       bbox_to_anchor = (1 + distance_plot_to_cbar, 0, 1, 1),
                       bbox_transform = ax.transAxes, borderpad = 0)

    if colorpalette == 'Classic-IR':

        # draw a colorbar with with a lowres warm range (= fewer gray levels) than the one used for the actual image #

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            norm_cbar = mpl.colors.BoundaryNorm(clevels_cbar, cmap_cbar.N)
            cbar_dummy_image = ax.pcolormesh(lons, lats, np.zeros_like(lons),
                                             cmap = cmap_cbar, norm = norm_cbar, transform = projection_regular,
                                             antialiased = False, visible = False)

        cbar = fig.colorbar(cbar_dummy_image, cax = axins, ticks = clevels_cbar[::10],
                            extend = 'both', extendfrac = 0.03)

    else:
        if cmap_num_colors_between <= 20:
            cmap_ticks_skipping_factor = 1
        elif cmap_num_colors_between <= 100:
            cmap_ticks_skipping_factor = 5
        else:
            cmap_ticks_skipping_factor = 10

        cbar = fig.colorbar(plotted_image, cax = axins, ticks = clevels[::cmap_ticks_skipping_factor],
                            extend = 'both', extendfrac = 0.03)


    # draw the image description #

    date_local = date_sensed
    timeshift_str = 'UTC'

    if mode == 'single_band':
        description = 'Band {:d} ({} {})'.format(band,
                       get_band_info(band, 'abbreviation'),
                       get_band_info(band, 'central_wavelength'))
        if band <= 6:
            if normalization == 'none':
                pass
            elif normalization == 'piecewise_linear':
                description += ' Normalization: Piecewise-Linear'
            elif normalization == 'max_storm_contrast':
                description += ' Normalization: Max Storm Contrast'

    elif mode == 'band_difference':
        description = 'Band Difference B{:02d}-B{:02d} '.format(band[0], band[1])

        description += '({}-{})'.format(
                        get_band_info(band[0], 'central_wavelength'),
                        get_band_info(band[1], 'central_wavelength'))

    elif mode == 'ndvi':
        description = 'NDVI'


    text_descr_str = 'GOES-16/ABI: {}   {:4d}-{:02d}-{:02d} {:02d}:{:02d}{}'.format(
                      description, date_local.year, date_local.month, date_local.day,
                      date_local.hour, date_local.minute, timeshift_str)
    ax.text(0.02, 0.02, text_descr_str, transform = ax.transAxes, color = 'white',
            horizontalalignment = 'left', verticalalignment = 'bottom', bbox=dict(facecolor='black', alpha=0.6))


    # finalize the plot #

    if render_type == 'png':
        fig.savefig(path['base'] + path['image'] + imagename)
        plt.close()

        # crop top and bottom whitespace of the png image with pillow #

        im = Image.open(path['base'] + path['image'] + imagename)
        image_array = np.asarray(im.convert('L'))
        image_array = np.where(image_array < 255, 1, 0)
        image_filter = np.amax(image_array, axis=1)
        vmargins = [np.nonzero(image_filter)[0][0], np.nonzero(image_filter[::-1])[0][0]]
        im_cropped = Image.new('RGB',(im.size[0], im.size[1] - vmargins[0] - vmargins[1] - 2), (255,255,255))
        im_cropped.paste(im.crop((0, vmargins[0] + 1, im.size[0], im.size[1] - vmargins[1] - 1)), (0, 0))
        im.close()
        im_cropped.save(path['base'] + path['image'] + imagename, 'png')
        im_cropped.close()

        return


    elif render_type == 'interactive':
        plt.show()
        plt.close()

        return


