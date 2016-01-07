#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'arnault'

import pymongo
import pyfits
import numpy
from bson import CodecOptions, SON
import glob
import re

CC = False

if CC:
    MONGO_URL = r'mongodb://lsst:lsst2015@172.17.0.190:27017/lsst'
    FILES = '/sps/lsst/data/CFHTLS/D2/*.fz'
else:
    MONGO_URL = r'mongodb://127.0.0.1:27017'
    FILES = 'data/*'

def fits_to_mongo(fits, name):
    hdulist = pyfits.open(name)
    hdulist.verify('silentfix')
    hdr = hdulist[0].header

    # print hdr.tostring(sep='\n', padding=False)

    # object = SON()
    object = dict()

    for k in hdr.keys():
        k = k.strip()
        if k == '':
            continue
        if k == 'COMMENT':
            continue
        if k == 'HISTORY':
            continue
        value = hdr.get(k)
        if isinstance(value, long):
            # value = str(value)
            try:
                x = str(value)
            except:
                print 'bad conversion'
                raise
        else:
            x = value
        # print k, value
        object[k] = x

    try:
        fits.insert_one(object)
    except Exception as e:
        print 'oups'
        print  e.message
        pass

    pass



if __name__ == '__main__':
    client = pymongo.MongoClient(MONGO_URL)

    # print client.database_names()

    # client.drop_database('lsst')

    lsst = client.lsst

    try:
        test = lsst.test
        lsst.drop_collection('test')
    except InvalidName as e:
        pass

    try:
        fits = lsst.fits
        lsst.drop_collection('fits')
    except InvalidName as e:
        pass

    opts = CodecOptions(document_class=SON)
    fits = lsst.create_collection('fits', codec_options=opts)

    for coll in lsst.collection_names():
        c = lsst[coll]
        print coll, c.count()

    for file in glob.glob(FILES):
        fits_to_mongo(fits, file)
        # break

    print fits.count()

    out = fits.find(SON({u'OBJECT': 'D2'}))
    for x in out:
        print x

