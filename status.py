#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'arnault'

import pymongo
import pyfits
import numpy
from bson import CodecOptions, SON
import glob
import os

CC = True

if os.name == 'nt':
    MONGO_URL = r'mongodb://127.0.0.1:27017'
    FILES_ROOT = 'data/'
else:
    MONGO_URL = r'mongodb://lsst:lsst2015@172.17.0.190:27017/lsst'
    FILES_ROOT = '/sps/lsst/data/CFHT/input/raw/'
    MONGO2_URL = r'mongodb://lsst:lsst2015@172.17.0.190:27017/snlsfits'

FILES = FILES_ROOT + '/*/*/*/*/*.fits.fz'


if __name__ == '__main__':
    client = pymongo.MongoClient(MONGO_URL)

    lsst = client.lsst

    print '------------lsst'
    c = lsst.fits
    print c.count()

    c.create_index( [ ('center', '2dsphere') ] )

    for o in c.find( { 'center' : { '$geoWithin': { '$centerSphere' : [ [ -145.0, 53.0 ], 1.0 ] } } } , {'_id':0, 'where':1, 'center':1 } ):
        print o

