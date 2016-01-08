import sys
import pymongo

MONGO_URL = r'mongodb://lsst:lsst2015@172.17.0.190:27017/lsst'
try:
        lsstDB = pymongo.MongoClient(MONGO_URL)
        myCollection = lsstDB.lsst.mycollection
        myDoc={}
        myDoc["test"]="test"
        insert_Document = myCollection.insert_one(myDoc)
        print(insert_Document) # return the document id
        for foundDoc in myCollection.find():
                print(foundDoc)
except pymongo.errors.ConnectionFailure, e:
        print "Could not connect to server: %s" %e
        print sys.exc_info()


