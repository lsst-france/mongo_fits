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

def fits_to_mongo(fits, name):
    hdulist = pyfits.open(FILES_ROOT + name)
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
        object['where'] = name.split('/')

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

    try:
        fits = lsst.fits
    except:
        pass
        opts = CodecOptions(document_class=SON)
        fits = lsst.create_collection('fits', codec_options=opts)

    for coll in lsst.collection_names():
        c = lsst[coll]
        print coll, c.count()

    # we killed at /sps/lsst/data/CFHT/input/raw/06AL01/D3/2006-06-02/g/850592p.fits.fz

    for file in glob.glob(FILES):
        file = file.replace('\\', '/')
        f = file.replace(FILES_ROOT, '')
        print 'existing file', f

        out = fits.find( { 'where': { '$in': [file.split('/')[-1]] } } )

        if out.count() == 0:
            print 'encode file', f
            fits_to_mongo(fits, f)
            pass
        else:
            print f, 'is encoded'
            for x in out:
                print x[u'where']

    print fits.count()

    out = fits.find( { 'where': { '$in': [u'732190p.fits.fz'] } } )
    for x in out:
        print x[u'where']

