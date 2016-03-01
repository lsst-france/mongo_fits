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
    for coll in lsst.collection_names():
        c = lsst[coll]
        print coll, c.count()
        '''
        {}
        { 'bottom_right.0' : { $gt: 214.9, $lt: 215.1 } }
        '''
        for o in c.find( { 'bottom_right.0' : { '$gt': 215.00000, '$lt': 215.20000 } }, {'_id':0, 'where':1 } ):
            print o



    client = pymongo.MongoClient(MONGO2_URL)
    lsst = client.snlsfits

    print '------------snlsfits'
    for coll in lsst.collection_names():
        c = lsst[coll]
        print coll, c.count()

        o = c.find_one()
        print o

