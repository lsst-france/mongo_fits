#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'arnault'

import pymongo
import pyfits
from bson import CodecOptions, SON

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

    fits.insert_one(object)


if __name__ == '__main__':
    client = pymongo.MongoClient()
    client.drop_database('LSST')
    lsst = client.LSST
    print lsst.collection_names()

    lsst.test.insert_many([{'i': i} for i in xrange(1000)]).inserted_ids
    print lsst.test.count()

    opts = CodecOptions(document_class=SON)
    fits = lsst['fits'].with_options(codec_options=opts)

    fits_to_mongo(fits, '/workspace/charm/PyPlot/doc/source/solutions/data/dss.19.59.54.3+09.59.20.9 4x2.fits')
    fits_to_mongo(fits, '/workspace/charm/PyPlot/doc/source/solutions/data/dss.19.59.54.3+09.59.20.9 10x10.fits')

    out = fits.find(SON({u'CNPIX1': 10292}))
    for x in out:
        print x
