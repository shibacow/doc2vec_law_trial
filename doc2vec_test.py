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
OUTPUT_MODEL = 'model/doc2vec.model.laws1'
SAMPLING=500
PASSING_PRECISION = int(0.80*SAMPLING)
from datetime import datetime
import random

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
    def __init__(self,tagger,elm,count):
        self.count=count
        self.tagger=tagger
        self.body=elm['body']
        self.title=elm['title']
        self.cat=elm['cat']
        strip_body=self.__strip_html(self.body)
        #self.sentence = self.__tokenized(strip_body)
        self.sentence = self.__tokenized_wakati(strip_body)
        #logging.info(self.strip_body)
    def __strip_html(self,body):
        d=pq(body)
        return d('body').text()
    def __tokenized_wakati(self,body):
        ps=self.tagger.parse(body)
        if not ps:
            return None
        words=ps.split(' ')
        logging.info("count={} name={} word={}".format(self.count,self.title,words[:20]))
        return TaggedDocument(words=words, tags=[self.cat])

    def __tokenized(self,body):
        ps=self.tagger.parse(body)
        if not ps:
            return None
        lines=ps.splitlines()
        words = []
        for line in lines:
            chunks = line.split('\t')
            if len(chunks) > 3 and chunks[3].startswith('名詞') and not chunks[3].startswith('名詞-数'):
                words.append(chunks[0])
        logging.info("count={} name={} word={}".format(self.count,self.title,words[:20]))
        return TaggedDocument(words=words, tags=[self.cat])

                    
def train(sentences):
    model = models.Doc2Vec(size=800, alpha=0.0015, sample=1e-4, min_count=0, workers=8)
    model.build_vocab(sentences)
    TOP_NUM=10
    train_log=open('log/train_{}.log'.format(datetime.now().strftime('%Y-%m-%d_%H%M')),'a')
    for x in range(30):
        logging.info("x={}".format(x))
        model.train(sentences,total_examples=model.corpus_count,epochs=model.iter)
        ranks = []
        for doc_id in range(SAMPLING):
            inferred_vector = model.infer_vector(sentences[doc_id].words)
            sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
            rank = [docid for docid, sim in sims].index(sentences[doc_id].tags[0])
            ranks.append(rank)
        cnt= collections.Counter(ranks)
        top=sum([v for k,v in cnt.items() if k<=TOP_NUM])
        logging.info("cnt={} top{}={} cnt={}".format(x,TOP_NUM,top,cnt))
        train_log.write("cnt={} top{}={} cnt={}\n".format(x,TOP_NUM,top,cnt))
        train_log.flush()
        if top >= PASSING_PRECISION:
            break
    train_log.close()
    return model

def main():
    mp=connect_mongo()
    #tagger = MeCab.Tagger('-Ochasen')
    tagger = MeCab.Tagger('-Owakati')
    sentences=[]
    pipeline=[{"$sample":{"size":300}}]
    #law_base=mp.base.aggregate(pipeline)
    law_base=mp.base.find()
    for i,a in enumerate(law_base):
        ol=OneLaw(tagger,a,i)
        if ol.sentence:
            sentences.append(ol.sentence)
    #random.shuffle(sentences)
    model=train(sentences)
    model.save(OUTPUT_MODEL)
if __name__=='__main__':main()
