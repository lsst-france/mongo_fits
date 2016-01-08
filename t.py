import pymongo


MONGO_URL = r'mongodb://lsst:lsst2015@ccosvm0950:27017/lsst'
lsstDB = pymongo.MongoClient(MONGO_URL)
myCollection = lsstDB.lsst.mycollection
myDoc={}
myDoc["test"]="test"
insert_Document = myCollection.insert_one(myDoc)
print(insert_document) # return the document id
for foundDoc in myCollection.find():
        print(foundDoc)


