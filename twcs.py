#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Load the WCS information from a fits header, and use it
# to convert pixel coordinates to world coordinates.

from __future__ import division # confidence high

import numpy as np
from astropy import wcs as pywcs
from astropy.io import fits
import re

class WCS:
    def __init__(self, header):
        self.xy0 = np.array([header['CRPIX1'], header['CRPIX2']])

        a = header['CD1_1']
        b = header['CD1_2']
        c = header['CRVAL1']
        d = header['CD2_1']
        e = header['CD2_2']
        f = header['CRVAL2']

        self.matrix = np.array([[a, b], [d, e]])
        self.rd0 = np.array([c, f])

    def xy_to_radec(self, xy):
        xy -= self.xy0
        rd = self.matrix.dot(xy) + self.rd0
        return rd

    def radec_to_xy(self, rd):
        tmat = self.matrix.conj()
        rd -= self.rd0
        xy = tmat.dot(rd) + self.xy0

        return xy


def read_hdus(fitsfile):
    """
    Get pixels from FITS file

    cf http://stsdas.stsci.edu/stsci_python_epydoc/pyfits/api_hdulists.html

    Return a HDUList()
    """
    hdus = None
    try:
        with fits.open(fitsfile) as data_fits:
            try:
                data_fits.verify('silentfix')
                return data_fits
            except ValueError as err:
                logging.error('Error: %s', err)
    except EnvironmentError as err:
        logging.error('Cannot open the data fits file. - %s', err)
    return hdus

# Load the FITS hdulist using pyfits
hdus = read_hdus('data/03BL01/D3/2004-01-13/i/732183p.fits.fz')

# Parse the WCS keywords in the primary HDU

for n in range(1, 36):
    print '--------------------------------'
    header = hdus[n].header
    wcs = pywcs.WCS(header)

    mywcs = WCS(header)

    # Some pixel coordinates of interest.
    detsize = header['DATASEC']
    m = re.match('[^\[]*\[([0-9]+):([0-9]+),([0-9]+):([0-9]+).*', detsize)
    low1 = int(m.group(1))
    high1 = int(m.group(2))
    low2 = int(m.group(3))
    high2 = int(m.group(4))

    low = [low1, low2]
    high = [high1, high2]

    pixel = np.array([low, high], np.float_)
    sky = wcs.wcs_pix2world(pixel, 0)

    rd_low = mywcs.xy_to_radec(low)
    rd_high = mywcs.xy_to_radec(high)

    # print low, high

    print 'mat=', rd_low, rd_high

    d_low  = sky[0] - rd_low
    d_high = sky[1] - rd_high

    print 'd  =', d_low, d_high

