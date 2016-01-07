#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'arnault'

import pymongo
import pyfits
from bson import CodecOptions, SON
import glob
import re

MONGO_URL = r'mongodb://lsst:lsst2015@172.17.0.190:27017/lsst'
MONGO_URL = r'mongodb://127.0.0.1:27017'


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
    # 'mongodb://user:' + password + '@127.0.0.1'
    # client = pymongo.MongoClient('134.158.246.25', 27017)
    client = pymongo.MongoClient('127.0.0.1', 27017)

    print client.database_names()

    # client.drop_database('lsst')

    lsst = client.lsst

    print lsst.collection_names()

    lsst.test.insert_many([{'i': i} for i in xrange(1000)]).inserted_ids
    print lsst.test.count()

    exit()

    opts = CodecOptions(document_class=SON)
    fits = lsst['fits'].with_options(codec_options=opts)

    for file in glob.glob('data/*.fz'):
        fits_to_mongo(fits, file)
        # exit ()

    out = fits.find(SON({u'CNPIX1': 10292}))
    for x in out:
        print x
