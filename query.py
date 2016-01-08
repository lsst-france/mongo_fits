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

FILES = FILES_ROOT + '/*/*/*/*/*.fits.fz'


if __name__ == '__main__':
    client = pymongo.MongoClient(MONGO_URL)

    lsst = client.lsst

    for coll in lsst.collection_names():
        c = lsst[coll]
        print coll, c.count()


    out = lsst.fits.find( { 'where': { '$in': [u'i'] } } )
    for x in out:
        print x[u'where']

