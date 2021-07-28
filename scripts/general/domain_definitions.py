
########################################################################################################################
###                                                                                                                  ###
###  This module uses a width of max. 120 characters                                                                 ###
###                                                                                                                  ###
###  Author: Marco Wurth, July 2021                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: None                                                                              ###
###                                                                                                                  ###
###  Content:                                                                                                        ###
###   The function in this module serves as a library for different domains that I used defined by a center          ###
###   coordinate and a radius in km around it                                                                        ###
###   Feel free to modify or add more domains!                                                                       ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   This module here containes functions that have to be imported by another function or script                    ###
###                                                                                                                  ###
########################################################################################################################


def get_image_domain(domain_name):

    if domain_name == 'GOES-East_fulldisk':
        domain =   dict(name = domain_name, limits_type = 'radius',
                        centerlat = 0, centerlon = -75.2, radius = 7450)

    elif domain_name == 'Atacama_Squared':
        domain =   dict(name = domain_name, limits_type = 'radius',
                        centerlat = -22.5, centerlon = -71.4, radius = 1000)

    elif domain_name == 'Atacama_Peru_West':
        domain =   dict(name = domain_name, limits_type = 'radius',
                        centerlat = -15.4, centerlon = -74.5, radius = 300)

    elif domain_name == 'Atacama_Peru_East':
        domain =   dict(name = domain_name, limits_type = 'radius',
                        centerlat = -17.4, centerlon = -71.8, radius = 300)

    elif domain_name == 'Atacama_Chile_North':
        domain =   dict(name = domain_name, limits_type = 'radius',
                        centerlat = -20.1, centerlon = -70.3, radius = 300)

    elif domain_name == 'Atacama_Chile_Central':
        domain =   dict(name = domain_name, limits_type = 'radius',
                        centerlat = -24.5, centerlon = -70.5, radius = 300)

    elif domain_name == 'Atacama_Chile_South':
        domain =   dict(name = domain_name, limits_type = 'radius',
                        centerlat = -29.0, centerlon = -71.3, radius = 300)

    elif domain_name == 'Argentina_Central':
        domain =   dict(name = domain_name, limits_type = 'radius',
                        centerlat = -34.6, centerlon = -64.4, radius = 800)

    elif domain_name == 'Argentina_Central_cerca':
        domain =   dict(name = domain_name, limits_type = 'radius',
                        centerlat = -36.0, centerlon = -66.0, radius = 500)

    else:
        print('domain unknown:', domain_name)
        exit()

    return domain
