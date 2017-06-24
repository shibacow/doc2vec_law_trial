#!/home/ubuntu/anaconda3/bin/python
# -*- coding: utf-8 -*-

import MeCab
import doc2vec_test
from gensim import models
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

model = models.Doc2Vec.load('model/doc2vec.model.laws7')

# 似た文章を探す
def search_similar_texts(law):
    logging.info(law)
    most_similar_texts = model.docvecs.most_similar(law)
    logging.info("="*30)
    if most_similar_texts:
        msg="base={}\n".format(law)
        for similar_text in most_similar_texts:
            msg+="\t\tsim_text={} match={}\n".format(similar_text[0],similar_text[1])
            #logging.info(msg)
            #logging.info(similar_text)
        logging.info(msg)
if __name__ == '__main__':
    mp=doc2vec_test.connect_mongo()
    catset=set()
    #for l in mp.base.aggregate([{"$sample":{"size":50}}]):
    #    t=l['cat']
    #    catset.add(t)
        #search_similar_texts(t)
    for c in mp.base.find({},{'cat':True}):
        t=c['cat']
        catset.add(t)
    for t in catset:
        search_similar_texts(t)
        
