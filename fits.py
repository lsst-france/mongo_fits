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

    for index, hdu in enumerate(hdulist):
        """ handle all hdus of this file """
        hdr = hdu.header

        wcs = pywcs.WCS(hdulist[0].header)

        """ just consider the header of this hdu """

        # print hdr.tostring(sep='\n', padding=False)

        object = SON()

        object['header_index'] = index
        object['where'] = name.split('/')

        thebytes = pickle.dumps(wcs, protocol=2)
        object['wcs'] = Binary(thebytes)

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

        break

    print '# of objects in collection', fits.count()

    out = fits.find( { 'where': { '$in': [u'732190p.fits.fz'] } } )
    for x in out:
        print x[u'where']

