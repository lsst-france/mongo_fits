#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'arnault'

import pymongo
import numpy as np
from bson import CodecOptions, SON, BSON
from bson.binary import Binary
import pickle
import glob
import os
from astropy import wcs as pywcs
from astropy.io import fits as pyfits
import re

CC = True

if os.name == 'nt':
    MONGO_URL = r'mongodb://127.0.0.1:27017'
    FILES_ROOT = 'data/'
else:
    MONGO_URL = r'mongodb://lsst:lsst2015@172.17.0.190:27017/lsst'
    FILES_ROOT = '/sps/lsst/data/CFHT/D3/input/raw/'

FILES = FILES_ROOT + '/*/*/*/*/*.fits.fz'

class MyWCS:
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

def get_corners(header, wcs, mywcs):
    detsize = header['DATASEC']
    m = re.match('[^\[]*\[([0-9]+):([0-9]+),([0-9]+):([0-9]+).*', detsize)
    low1 = np.float64(m.group(1))
    high1 = np.float64(m.group(2))
    low2 = np.float64(m.group(3))
    high2 = np.float64(m.group(4))
    low = [low1, low2]
    high = [high1, high2]

    pixel = np.array([low, high], np.float64)

    try:
        sky = wcs.wcs_pix2world(pixel, 0)
    except:
        print "Unexpected error:", sys.exc_info()[0]

    ra_dec_low = mywcs.xy_to_radec(low)
    ra_dec_high = mywcs.xy_to_radec(high)

    # print 'low=', low, 'high=', high

    # print 'mat=', ra_dec_low, ra_dec_high
    # print 'wcs=', sky[0], sky[1]

    d_low  = (sky[0] - ra_dec_low)/sky[0]
    d_high = (sky[1] - ra_dec_high)/sky[1]

    # print 'd  =', d_low, d_high

    return (ra_dec_low[0], ra_dec_low[1]), (ra_dec_high[0], ra_dec_high[1])


def read_hdus(fitsfile):
    """ pixels from FITS file

    cf http://stsdas.stsci.edu/stsci_python_epydoc/pyfits/api_hdulists.html

    Return a HDUList()
    """
    data_fits = None
    try:
        with pyfits.open(fitsfile) as data_fits:
            try:
                data_fits.verify('silentfix')
                return data_fits
            except ValueError as err:
                print 'Error: %s' % err
    except EnvironmentError as err:
        print 'Cannot open the data fits file. - %s' % err
    return data_fits

class PointRange:
    def __init__(self):
        self.min_ra = None
        self.max_ra = None
        self.min_dec = None
        self.max_dec = None

    def update(self, ra_dec):
        ra = ra_dec[0]
        dec = ra_dec[1]

        changed = False
        if self.min_ra is None or ra < self.min_ra:
            changed = True
            self.min_ra = ra
            
        if self.max_ra is None or ra > self.max_ra:
            changed = True
            self.max_ra = ra

        if self.min_dec is None or dec < self.min_dec:
            changed = True
            self.min_dec = dec

        if self.max_dec is None or dec > self.max_dec:
            changed = True
            self.max_dec = dec

        if changed:
            self.show()

    def show(self):
        print 'Range: RA=[%f %f] DEC=[%f %f]' % (self.min_ra, self.max_ra, self.min_dec, self.max_dec)


myrange = PointRange()

def fits_to_mongo(fits, name):
    global myrange

    # print FILES_ROOT + name

    hdulist = read_hdus(FILES_ROOT + name)

    for index, hdu in enumerate(hdulist):
        """ handle all hdus of this file """
        hdr = hdu.header

        ra_dec0, ra_dec1 = None, None

        wcs = pywcs.WCS(hdr)
        try:
            mywcs = MyWCS(hdr)
            ra_dec0, ra_dec1 = get_corners(hdr, wcs, mywcs)
            myrange.update(ra_dec0)
            myrange.update(ra_dec1)

        except:
            # print 'no WCS data in this header'
            pass

        """ just consider the header of this hdu """

        # print hdr.tostring(sep='\n', padding=False)

        object = SON()

        object['header_index'] = index
        object['where'] = name.split('/')

        thebytes = pickle.dumps(wcs, protocol=2)
        object['wcs'] = Binary(thebytes)
        object['corners'] = (ra_dec0, ra_dec1)

        for card in hdr._cards:
            comment = card.comment
            key = card.keyword
            value = card.value
            # print '[%s] = [%s] | %s' % (key, value, comment)
            if key == '':
                continue
            if key == 'COMMENT':
                continue
                pass
            if key == 'HISTORY':
                continue
                pass
            if isinstance(value, long):
                value = str(value)

            # print key, value
            object[key] = (value, comment)

        try:
            fits.insert_one(object)
        except Exception as e:
            print 'oups'
            print  e.message
            pass

    pass



if __name__ == '__main__':
    client = pymongo.MongoClient(MONGO_URL)

    lsst = client.lsst

    recreate = True

    if recreate:
        try:
            fits = lsst.fits
            lsst.drop_collection('fits')
        except:
            pass

    try:
        fits = lsst.fits
    except:
        opts = CodecOptions(document_class=SON)
        fits = lsst.create_collection('fits', codec_options=opts)

    for coll in lsst.collection_names():
        c = lsst[coll]
        print coll, c.count()

    # we killed at /sps/lsst/data/CFHT/input/raw/06AL01/D3/2006-06-02/g/850592p.fits.fz

    for file in glob.glob(FILES):
        file = file.replace('\\', '/')
        f = file.replace(FILES_ROOT, '')
        # print 'existing file', f

        out = fits.find( { 'where': { '$in': [file.split('/')[-1]] } } )

        if out.count() == 0:
            # print 'encode file', f
            fits_to_mongo(fits, f)
            pass
        else:
            # print f, 'is encoded'
            for x in out:
                print x[u'where']

    print '# of objects in collection', fits.count()

    out = fits.find( { 'where': { '$in': [u'732190p.fits.fz'] } } )
    for x in out:
        print x[u'where']

