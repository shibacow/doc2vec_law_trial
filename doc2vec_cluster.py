#!/home/ubuntu/anaconda3/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from gensim import models
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

MODEL_PATH="model/doc2vec.model.laws7"
model = models.Doc2Vec.load(MODEL_PATH)

class MongoOp(object):
    def __init__(self,host='localhost'):
        self.mp = MongoClient(host, 27017)
        self.laws=self.mp.laws
        self.base=self.laws.base
    def __del__(self):
        if self.mp:
            self.mp.close()
def connect_mongo():
    return MongoOp('localhost')

def get_cat():
    catset=set()
    mp=connect_mongo()
    pipeline=[{"$group":{"_id":"$cat"}}]
    r=mp.base.aggregate(pipeline)
    for c in r:
        catset.add(c['_id'])
def eval(catset):
    for f in catset:
        for e in catset:
def main():
    catset=get_cat()
    
if __name__=='__main__':main()
