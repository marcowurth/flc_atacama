
########################################################################################################################
###                                                                                                                  ###
###  This module uses a width of max. 120 characters                                                                 ###
###                                                                                                                  ###
###  Author: Marco Wurth, July 2021                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: numpy, matplotlib, palettable                                                     ###
###                                                                                                                  ###
###  Content:                                                                                                        ###
###   The function in this module generates and returns a matplotlib cmap and 1D ndarray with the colorbar levels    ###
###   The cmap includes two colors for over and under the highest and lowest clevel                                  ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   This module here containes functions that have to be imported by another function or script                    ###
###                                                                                                                  ###
########################################################################################################################

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import palettable


def generate_cmap(path, colorpalette, cmap_reversed, missing_value_color,
                  cmap_num_colors_between, cmap_range_min, cmap_range_max,
                  lowres_classic_ir_cbar = False):

    if colorpalette == 'Classic-IR':
        if lowres_classic_ir_cbar:
            filename_colorpalette = 'rainbowIRsummer.txt'
            with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
                lines = f.readlines()
            rgb_colors = []
            rgb_colors.append([float(lines[70][:10]), float(lines[70][11:21]), float(lines[70][22:32])])
            for i, line in enumerate(lines):
                if i % 14 == 0 and i > 70:
                    rgb_colors.append([float(line[:10]), float(line[11:21]), float(line[22:32])])
            for j in range(30):
                rgb_colors.append(list(palettable.cmocean.sequential.Gray_20.get_mpl_colormap(
                                        N = 30).reversed()(j)[:3]))
            cmap_cbar = mpl.colors.ListedColormap(np.array(rgb_colors), name='Classic IR Colormap with Lowres Warm Range')\
                         .with_extremes(bad = missing_value_color, under = rgb_colors[0], over = rgb_colors[-1])
            clevels_cbar = np.array(list(np.arange(-90, -20, 1)) + list(np.arange(-20, 40+1, 2)))

            return cmap_cbar, clevels_cbar

        else:
            filename_colorpalette = 'rainbowIRsummer.txt'
            with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
                lines = f.readlines()
            rgb_colors = []
            rgb_colors.append([float(lines[70][:10]), float(lines[70][11:21]), float(lines[70][22:32])])
            for i, line in enumerate(lines):
                if i % 14 == 0 and i > 70:
                    rgb_colors.append([float(line[:10]), float(line[11:21]), float(line[22:32])])
            num_bw_colors = int(60 / 0.1)
            for j in range(num_bw_colors):
                rgb_colors.append(list(palettable.cmocean.sequential.Gray_20.get_mpl_colormap(
                                        N = num_bw_colors).reversed()(j)[:3]))
            cmap = mpl.colors.ListedColormap(np.array(rgb_colors), name = 'Classic IR Colormap with Highres Warm Range')\
                    .with_extremes(bad = missing_value_color, under = rgb_colors[0], over = rgb_colors[-1])
            clevels = np.array(list(np.arange(-90, -20, 1)) + list(np.arange(-20, 40+.01, 0.1)))

            return cmap, clevels, colorpalette


    else:
        rgb_colors = []

        # single colorpalettes #

        if colorpalette == 'viridis':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(plt.get_cmap(colorpalette, cmap_num_colors_between + 2)(i)[:3]))
        if colorpalette == 'plasma':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(plt.get_cmap(colorpalette, cmap_num_colors_between + 2)(i)[:3]))
        if colorpalette == 'inferno':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(plt.get_cmap(colorpalette, cmap_num_colors_between + 2)(i)[:3]))
        if colorpalette == 'magma':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(plt.get_cmap(colorpalette, cmap_num_colors_between + 2)(i)[:3]))
        if colorpalette == 'cividis':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(plt.get_cmap(colorpalette, cmap_num_colors_between + 2)(i)[:3]))

        if colorpalette == 'Gray_BW':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(palettable.cmocean.sequential.Gray_20.get_mpl_colormap(
                                        N = cmap_num_colors_between + 2)(i)[:3]))
        elif colorpalette == 'Hawaii':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(palettable.scientific.sequential.Hawaii_20.get_mpl_colormap(
                                        N = cmap_num_colors_between + 2)(i)[:3]))
        elif colorpalette == 'LaJolla':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(palettable.scientific.sequential.LaJolla_20.get_mpl_colormap(
                                        N = cmap_num_colors_between + 2)(i)[:3]))
        elif colorpalette == 'LaPaz':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(palettable.scientific.sequential.LaPaz_20.get_mpl_colormap(
                                        N = cmap_num_colors_between + 2)(i)[:3]))
        elif colorpalette == 'Oslo':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(palettable.scientific.sequential.Oslo_20.get_mpl_colormap(
                                        N = cmap_num_colors_between + 2)(i)[:3]))
        elif colorpalette == 'Bilbao':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(palettable.scientific.sequential.Bilbao_20.get_mpl_colormap(
                                        N = cmap_num_colors_between + 2)(i)[:3]))
        elif colorpalette == 'Roma':
            for i in range(cmap_num_colors_between + 2):
                rgb_colors.append(list(palettable.scientific.diverging.Roma_20.get_mpl_colormap(
                                        N = cmap_num_colors_between + 2)(i)[:3]))

        # double colorpalettes #

        elif colorpalette == 'LaJolla+Oslo':
            for i in range(cmap_num_colors_between // 2 + 1):
                rgb_colors.append(list(palettable.scientific.sequential.Oslo_20.get_mpl_colormap(
                                        N = cmap_num_colors_between // 2 + 1)(i)[:3]))
            for i in range(cmap_num_colors_between // 2 + 1):
                rgb_colors.append(list(palettable.scientific.sequential.LaJolla_20.get_mpl_colormap(
                                        N = cmap_num_colors_between // 2 + 1)(i)[:3]))
        elif colorpalette == 'Oslo+LaJolla':
            for i in range(cmap_num_colors_between // 2 + 1):
                rgb_colors.append(list(palettable.scientific.sequential.LaJolla_20.get_mpl_colormap(
                                        N = cmap_num_colors_between // 2 + 1)(i)[:3]))
            for i in range(cmap_num_colors_between // 2 + 1):
                rgb_colors.append(list(palettable.scientific.sequential.Oslo_20.get_mpl_colormap(
                                        N = cmap_num_colors_between // 2 + 1)(i)[:3]))
        elif colorpalette == 'LaJolla+Devon':
            for i in range(cmap_num_colors_between // 2 + 1):
                rgb_colors.append(list(palettable.scientific.sequential.Devon_20.get_mpl_colormap(
                                        N = cmap_num_colors_between // 2 + 1)(i)[:3]))
            for i in range(cmap_num_colors_between // 2 + 1):
                rgb_colors.append(list(palettable.scientific.sequential.LaJolla_20.get_mpl_colormap(
                                        N = cmap_num_colors_between // 2 + 1)(i)[:3]))
        elif colorpalette == 'Bilbao+Devon':
            for i in range(cmap_num_colors_between // 2 + 1):
                rgb_colors.append(list(palettable.scientific.sequential.Devon_20.get_mpl_colormap(
                                        N = cmap_num_colors_between // 2 + 1)(i)[:3]))
            for i in range(cmap_num_colors_between // 2 + 1):
                rgb_colors.append(list(palettable.scientific.sequential.Bilbao_20.get_mpl_colormap(
                                        N = cmap_num_colors_between // 2 + 1)(i)[:3]))

        if cmap_reversed:
            rgb_colors = rgb_colors[::-1]
            cmap_str = colorpalette + '-reversed'
        else:
            cmap_str = colorpalette

        cmap = mpl.colors.ListedColormap(np.array(rgb_colors[1:-1]), name = colorpalette)\
                .with_extremes(bad = missing_value_color, under = rgb_colors[0], over = rgb_colors[-1])

        clevels = np.linspace(cmap_range_min, cmap_range_max, cmap_num_colors_between + 1)

        return cmap, clevels, cmap_str
