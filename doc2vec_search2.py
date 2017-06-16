#!/home/ubuntu/anaconda3/bin/python
# -*- coding: utf-8 -*-

import MeCab
import doc2vec_test
from gensim import models
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

model = models.Doc2Vec.load('model/doc2vec.model.laws3')

# 似た文章を探す
def search_similar_texts(law):
    most_similar_texts = model.docvecs.most_similar(law)
    logging.info("="*100)
    for similar_text in most_similar_texts:
        msg="base={} sim_text={} match={}".format(law,similar_text[0],similar_text[1])
        logging.info(msg)
if __name__ == '__main__':
    mp=doc2vec_test.connect_mongo()
    for l in mp.base.aggregate([{"$sample":{"size":100}}]):
        t=l['title']
        search_similar_texts(t)
