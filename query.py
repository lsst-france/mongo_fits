#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'arnault'

import pymongo
import numpy as np
import os
import pickle
from astropy import wcs as pywcs


if os.name == 'nt':
    MONGO_URL = r'mongodb://127.0.0.1:27017'
    FILES_ROOT = 'data/'
else:
    MONGO_URL = r'mongodb://lsst:lsst2015@172.17.0.190:27017/lsst'
    FILES_ROOT = '/sps/lsst/data/CFHT/input/raw/'



def dms(angle):
    """
    Convert a floating point angle into textual representation Degree:Minute:Second (-> DEC coordinate)
    :param angle: floating point value
    :return: Degree:Minute:Second
    """
    d = int(angle)
    m = (angle - d) * 60.0
    s = (m - int(m)) * 60.0
    return '[%d:%d:%f]' % (int(d), int(m), s)


def hms(angle):
    """
    Convert a floating point angle into textual representation Hour:Minute:Second (-> RA coordinate)
    :param angle: floating point value
    :return: Hour:Minute:Second
    """
    """  """
    hour = angle*24.0/360.0
    h = int(hour)
    m = (hour - h) * 60.0
    s = (m - int(m)) * 60.0
    return '[%d:%d:%f]' % (int(h), int(m), s)


def radec(coord):
    """
    Convert a floating point array of coordinates into textual representation Hour:Minute:Second (-> RA/DEC coordinates)
    :param coord: array of coordinates [RA, DEC]
    :return: text
    """
    return 'RA=%s DEC=%s' % (hms(coord[0]), dms(coord[1]))


if __name__ == '__main__':
    client = pymongo.MongoClient(MONGO_URL)

    lsst = client.lsst

    for coll in lsst.collection_names():
        c = lsst[coll]
        print coll, c.count()

    out = lsst.fits.find( { 'where': { '$in': [u'i'] } } )
    for x in out:
        print '---------- where    =', x[u'where'], x['header_index']
        print 'DETSIZE  = ', x['DETSIZE']
        for a in 'CD1_1', 'CD1_2', 'CD2_1', 'CD2_2', 'CRVAL1', 'CRVAL2', 'CRPIX1', 'CRPIX2':
            if a in x: print '%s = %s' % (a, x[a])
        path = FILES_ROOT + '/'.join(x[u'where'])
        print path

        for key in x:

            if key == 'wcs':
                value = x[key]
                try:
                    wcs = pickle.loads(value)

                    pixel = np.array([[0, 0],], np.float_)
                    sky = wcs.wcs_pix2world(pixel, 0)
                    ra, dec = sky[0]

                    # print 'RADEC', ra, dec

                except:
                    raise
            else:
                # print key, x[key]
                pass


        continue

