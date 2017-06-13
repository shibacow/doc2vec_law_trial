#!/home/ubuntu/anaconda3/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import MeCab
import collections
from gensim import models
from gensim.models.doc2vec import TaggedDocument
from pymongo import MongoClient
import re
import logging
from pyquery import PyQuery as pq
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
OUTPUT_MODEL = 'doc2vec.model.laws.gaiji'
PASSING_PRECISION = 93

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

class OneLaw(object):
    def __init__(self,tagger,elm):
        self.tagger=tagger
        self.body=elm['body']
        self.title=elm['title']
        self.cat=elm['cat']
        strip_body=self.__strip_html(self.body)
        self.sentence = self.__tokenized(strip_body)
        #logging.info(self.strip_body)
    def __strip_html(self,body):
        d=pq(body)
        return d('body').text()
    def __tokenized(self,body):
        lines=self.tagger.parse(body).splitlines()
        words = []
        for line in lines:
            chunks = line.split('\t')
            if len(chunks) > 3 and (chunks[3].startswith('動詞') or chunks[3].startswith('形容詞') or (chunks[3].startswith('名詞') and not chunks[3].startswith('名詞-数'))):
                words.append(chunks[0])
        logging.info("name={} word={}".format(self.title,words[:200]))
        return TaggedDocument(words=words, tags=[self.title])

def train(sentences):
    model = models.Doc2Vec(size=400, alpha=0.0015, sample=1e-4, min_count=1, workers=4)
    model.build_vocab(sentences)
    for x in range(100):
        print(x)
        model.train(sentences)
        ranks = []
        for doc_id in range(50):
            inferred_vector = model.infer_vector(sentences[doc_id].words)
            sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
            rank = [docid for docid, sim in sims].index(sentences[doc_id].tags[0])
            ranks.append(rank)
        print(collections.Counter(ranks))
        if collections.Counter(ranks)[0] >= PASSING_PRECISION:
            break
    return model

def main():
    mp=connect_mongo()
    tagger = MeCab.Tagger('-Ochasen')
    sentences=[]
    for a in mp.base.find({'cat':"外事"}):
        ol=OneLaw(tagger,a)
        sentences.append(ol.sentence)
    train(sentences)
    model.save(OUTPUT_MODEL)
if __name__=='__main__':main()
