
########################################################################################################################
###                                                                                                                  ###
###  This script/module uses a width of max. 120 characters                                                          ###
###                                                                                                                  ###
###  Tested with Python 3.9 and Fedora Linux                                                                         ###
###  Non-standard packages needed: numpy                                                                             ###
###                                                                                                                  ###
###  Content:                                                                                                        ###
###   The function in this module calculates an 2D ndarray of the solar zenith angle depending on a single date      ###
###   and latitude and longitude arrays                                                                              ###
###                                                                                                                  ###
###  Usage:                                                                                                          ###
###   This module here containes functions that have to be imported by another function or script                    ###
###                                                                                                                  ###
########################################################################################################################

import datetime

import numpy as np


def main():

    # example usage of function calc_sza()

    date = datetime.datetime(2020, 12, 7, 17, 0, 0)  # 6th April 2017 09:30:00 UTC

    # grid dimensions
    Nlats = 10
    Nlons = 10

    lat, lon = np.linspace(20.0, 30.0, Nlats + 1), np.linspace(-30.0, -10.0, Nlons + 1)  # grid boundaries
    latC, lonC = 0.5 * (lat[:-1] + lat[1:]), 0.5 * (lon[:-1] + lon[1:])  # center points
    latgrid, longrid = np.meshgrid(latC, lonC)

    print(latgrid.shape)
    print(longrid.shape)
    sza = calc_sza(date, longrid, latgrid)
    print(sza.shape)
    print(sza.min(), sza.max())

    return

############################################################################
############################################################################

# code from https://gist.github.com/anttilipp/1c482c8cc529918b7b973339f8c28895

'''
DEMO TO COMPUTE SOLAR ZENITH ANGLE
version 6 April 2017
by Antti Lipponen

Copyright (c) 2017 Antti Lipponen

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

############################################################################
# FUNCTION TO COMPUTE SOLAR AZIMUTH AND ZENITH ANGLE
# translated to Python from http://www.psa.es/sdg/sunpos.htm
############################################################################

def calc_sza(date, dLongitude, dLatitude):

    dHours, dMinutes, dSeconds = date.hour, date.minute, date.second
    iYear, iMonth, iDay = date.year, date.month, date.day

    dEarthMeanRadius = 6371.01
    dAstronomicalUnit = 149597890

    ###################################################################
    # Calculate difference in days between the current Julian Day
    # and JD 2451545.0, which is noon 1 January 2000 Universal Time
    ###################################################################
    # Calculate time of the day in UT decimal hours
    dDecimalHours = dHours + (dMinutes + dSeconds / 60.) / 60.
    # Calculate current Julian Day
    liAux1 = int((iMonth - 14.) / 12.)
    liAux2 = int((1461. * (iYear + 4800. + liAux1)) / 4.) \
            + int((367. * (iMonth - 2. - 12. * liAux1)) / 12.) \
            - int((3. * int((iYear + 4900. + liAux1) / 100.)) / 4.) \
            + iDay - 32075.
    dJulianDate = liAux2 - 0.5 + dDecimalHours / 24.
    # Calculate difference between current Julian Day and JD 2451545.0
    dElapsedJulianDays = dJulianDate - 2451545.0

    ###################################################################
    # Calculate ecliptic coordinates (ecliptic longitude and obliquity of the
    # ecliptic in radians but without limiting the angle to be less than 2*Pi
    # (i.e., the result may be greater than 2*Pi)
    ###################################################################
    dOmega = 2.1429 - 0.0010394594 * dElapsedJulianDays
    dMeanLongitude = 4.8950630 + 0.017202791698 * dElapsedJulianDays  # Radians
    dMeanAnomaly = 6.2400600 + 0.0172019699 * dElapsedJulianDays
    dEclipticLongitude = dMeanLongitude + 0.03341607 * np.sin(dMeanAnomaly)\
                        + 0.00034894 * np.sin(2. * dMeanAnomaly) - 0.0001134 - 0.0000203 * np.sin(dOmega)
    dEclipticObliquity = 0.4090928 - 6.2140e-9 * dElapsedJulianDays + 0.0000396 * np.cos(dOmega)

    ###################################################################
    # Calculate celestial coordinates ( right ascension and declination ) in radians
    # but without limiting the angle to be less than 2*Pi (i.e., the result may be
    # greater than 2*Pi)
    ###################################################################
    dSin_EclipticLongitude = np.sin(dEclipticLongitude)
    dY = np.cos(dEclipticObliquity) * dSin_EclipticLongitude
    dX = np.cos(dEclipticLongitude)
    dRightAscension = np.arctan2(dY, dX)
    if dRightAscension < 0.0:
        dRightAscension = dRightAscension + 2.0 * np.pi
    dDeclination = np.arcsin(np.sin(dEclipticObliquity) * dSin_EclipticLongitude)

    ###################################################################
    # Calculate local coordinates ( azimuth and zenith angle ) in degrees
    ###################################################################
    dGreenwichMeanSiderealTime = 6.6974243242 + 0.0657098283 * dElapsedJulianDays + dDecimalHours
    dLocalMeanSiderealTime = (dGreenwichMeanSiderealTime * 15. + dLongitude) * (np.pi / 180.)
    dHourAngle = dLocalMeanSiderealTime - dRightAscension
    dLatitudeInRadians = dLatitude * (np.pi / 180.)
    dCos_Latitude = np.cos(dLatitudeInRadians)
    dSin_Latitude = np.sin(dLatitudeInRadians)
    dCos_HourAngle = np.cos(dHourAngle)
    dZenithAngle = (np.arccos(dCos_Latitude * dCos_HourAngle * np.cos(dDeclination) \
                                + np.sin(dDeclination) * dSin_Latitude))
    #dY = -np.sin(dHourAngle)
    #dX = np.tan(dDeclination) * dCos_Latitude - dSin_Latitude * dCos_HourAngle
    #dAzimuth = np.arctan2(dY, dX)
    #dAzimuth[dAzimuth < 0.0] = dAzimuth[dAzimuth < 0.0] + 2.0 * np.pi
    #dAzimuth = dAzimuth / (np.pi / 180.)

    # Parallax Correction
    dParallax = (dEarthMeanRadius / dAstronomicalUnit) * np.sin(dZenithAngle)
    dZenithAngle = (dZenithAngle + dParallax) / (np.pi / 180.)

    return dZenithAngle

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
        print('total script time:  {:4f}s'.format(delta_t))
    elif 60 <= delta_t <= 3600:
        print('total script time:  {:.0f}min{:.0f}s'.format(delta_t//60, delta_t-delta_t//60*60))
    else:
        print('total script time:  {:.0f}h{:.0f}min'.format(delta_t//3600, (delta_t-delta_t//3600*3600)/60))
