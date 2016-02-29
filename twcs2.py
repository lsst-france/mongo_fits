#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Load the WCS information from a fits header, and use it
# to convert pixel coordinates to world coordinates.

from __future__ import division # confidence high

import numpy as np
from astropy import wcs as pywcs
from astropy.io import fits
import re
import os

class WCS:
    """
    Class to implement the transformation algorithm to convert pixel coordinate into WCS coordinates
    this reflects what is provided in the wcslib module
    """
    def __init__(self, header):
        """
        Constructor: fetch all WCS information to setup parameters needed for the
        conversion algorithm

        :param header: this is the FITS header
        :return: Nonz
        """

        CRPIX1 = header['CRPIX1']
        CRPIX2 = header['CRPIX2']

        CD1_1  = header['CD1_1']
        CD1_2  = header['CD1_2']
        CRVAL1 = header['CRVAL1']
        CD2_1  = header['CD2_1']
        CD2_2  = header['CD2_2']
        CRVAL2 = header['CRVAL2']

        # prepare the transfromation matrix

        self.xy0 = np.array([CRPIX1, CRPIX2], np.float64)

        a = CD1_1
        b = CD1_2
        c = CRVAL1
        d = CD2_1
        e = CD2_2
        f = CRVAL2

        self.matrix = np.array([[a, b], [d, e]], np.float64)
        self.ra_dec0 = np.array([c, f], np.float64)


    def xy_to_radec(self, xy):
        """
        Function to convert a pixel coordinates into a WCS coordonates

        :param xy: a 1D ndarray
        :return: ra_dec the result of the conversion as a 1d-array
        """

        xy -= self.xy0

        ra_dec = self.matrix.dot(xy)

        dec = self.ra_dec0[1] + ra_dec[1]
        dec_radians = 2.0 * np.pi * dec/360.0

        scale = np.array([np.cos(dec_radians), 1.0])

        ra_dec /= scale
        ra_dec += self.ra_dec0

        return ra_dec

    def radec_to_xy(self, ra_dec):
        # not yet done
        return None


def read_hdus(fitsfile):
    """ pixels from FITS file

    cf http://stsdas.stsci.edu/stsci_python_epydoc/pyfits/api_hdulists.html

    Return a HDUList()
    """
    data_fits = None
    try:
        with fits.open(fitsfile) as data_fits:
            try:
                data_fits.verify('silentfix')
                return data_fits
            except ValueError as err:
                print 'Error: %s' % err
    except EnvironmentError as err:
        print 'Cannot open the data fits file. - %s' % err
    return data_fits

# Load the FITS hdulist using pyfits
if os.name == 'nt':
    file_path = 'data/'
else:
    file_path = '/sps/lsst/data/CFHT/D3/input/raw/'

file_name = file_path + '/03BL01/D3/2004-01-13/i/732183p.fits.fz'

# Parse the WCS keywords in the primary HDU

for n in range(1, 36):
    print '--------------------------------'
    header = hdus[n].header
    wcs = pywcs.WCS(header)

    mywcs = WCS(header)

    # Some pixel coordinates of interest.
    detsize = header['DATASEC']
    m = re.match('[^\[]*\[([0-9]+):([0-9]+),([0-9]+):([0-9]+).*', detsize)
    low1 = np.float64(m.group(1))
    high1 = np.float64(m.group(2))
    low2 = np.float64(m.group(3))
    high2 = np.float64(m.group(4))

    low = [low1, low2]
    high = [high1, high2]

    pixel = np.array([low, high], np.float64)
    sky = wcs.wcs_pix2world(pixel, 0)

    ra_dec_low = mywcs.xy_to_radec(low)
    ra_dec_high = mywcs.xy_to_radec(high)

    # print 'low=', low, 'high=', high

    print 'mat=', ra_dec_low, ra_dec_high
    print 'wcs=', sky[0], sky[1]

    d_low  = (sky[0] - ra_dec_low)/sky[0]
    d_high = (sky[1] - ra_dec_high)/sky[1]

    print 'd  =', d_low, d_high


