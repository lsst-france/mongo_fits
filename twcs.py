#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Load the WCS information from a fits header, and use it
# to convert pixel coordinates to world coordinates.

from __future__ import division # confidence high

import numpy
import pywcs
import pyfits
import re

def xy_to_radec(header, X, Y):
    x0 = header['CRPIX1']
    y0 = header['CRPIX2']

    a = header['CD1_1']
    b = header['CD1_2']
    c = header['CRVAL1']
    d = header['CD2_1']
    e = header['CD2_2']
    f = header['CRVAL2']

    x = X - x0
    y = Y - y0

    ra = (a*x + b*y) + c
    dec = (d*x + e*y) + f

    return ra, dec

def radec_to_xy(header, ra, dec):
    x0 = header['CRPIX1']
    y0 = header['CRPIX2']

    a = header['CD1_1']
    b = header['CD1_2']
    c = header['CRVAL1']
    d = header['CD2_1']
    e = header['CD2_2']
    f = header['CRVAL2']

    numerator = b*d - a*e

    x = (b*f - e*c) / numerator
    y = (d*c - a*f) / numerator

    x += x0
    y += y0

    return x, y

# Load the FITS hdulist using pyfits
hdulist = pyfits.open('data/03BL01/D3/2004-01-13/i/732183p.fits.fz')

# Parse the WCS keywords in the primary HDU

for n in range(1, 36):
    header = hdulist[n].header
    wcs = pywcs.WCS(header)

    # Print out the "name" of the WCS, as defined in the FITS header
    # print wcs.wcs.name

    # Print out all of the settings that were parsed from the header
    # print '---------------------'
    # print wcs.wcs
    # print '---------------------'

    # Some pixel coordinates of interest.
    detsize = header['DETSIZE']
    m = re.match('[^\[]*\[([0-9]+):([0-9]+),([0-9]+):([0-9]+).*', detsize)
    low1 = int(m.group(1))
    high1 = int(m.group(2))
    low2 = int(m.group(3))
    high2 = int(m.group(4))

    ra1, dec1 = xy_to_radec(header, low1, low2)

    ra2, dec2 = xy_to_radec(header, high1, high2)
    print detsize, ra1, dec1, ra2, dec2
