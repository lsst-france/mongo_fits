#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'arnault'

import pymongo
import pyfits
from bson import CodecOptions, SON
import glob
import re

CC = True

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

    object = SON()

    for k in hdr.keys():
        if k == '':
            continue
        value = hdr.get(k)
        object[k] = value

    try:
        fits.insert_one(object)
    except Exception as e:
        print  e.message

    pass



if __name__ == '__main__':
    client = pymongo.MongoClient(MONGO_URL)

    # print client.database_names()

    # client.drop_database('lsst')

    lsst = client.lsst

    for coll in lsst.collection_names():
        c = lsst[coll]
        print coll, c.count()

    # lsst.test.insert_many([{'i': i} for i in xrange(1000)]).inserted_ids
    # print lsst.test.count()

    opts = CodecOptions(document_class=SON)
    fits = lsst.fits.with_options(codec_options=opts)

    for coll in lsst.collection_names():
        c = lsst[coll]
        print coll, c.count()

    exit()


    for file in glob.glob(FILES):
        fits_to_mongo(fits, file)
        break

    print fits.count()

    out = fits.find(SON({u'CNPIX1': 10292}))
    for x in out:
        print x

