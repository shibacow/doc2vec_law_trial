#!/home/ubuntu/anaconda3/bin/python
# -*- coding: utf-8 -*-

import MeCab
from gensim import models
from gensim.models.doc2vec import TaggedDocument
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

MODEL_PATH="doc2vec.model.laws"
model = models.Doc2Vec.load(MODEL_PATH)

# 似た文章を探す
def search_similar_texts(words):
    x = model.infer_vector(words)
    most_similar_texts = model.docvecs.most_similar([x])
    for similar_text in most_similar_texts:
        print(similar_text[0])

# 似た単語を探す
def search_similar_words(words):
    for word in words:
        print()
        print(word + ':')
        for result in model.most_similar(positive=word, topn=10):
            print(result[0])

def split_into_words(doc, name=''):
    mecab = MeCab.Tagger("-Ochasen")
    valid_doc = doc
    lines = mecab.parse(doc).splitlines()
    words = []
    for line in lines:
        chunks = line.split('\t')
        if len(chunks) > 3 and (chunks[3].startswith('動詞') or chunks[3].startswith('形容詞') or (chunks[3].startswith('名詞') and not chunks[3].startswith('名詞-数'))):
            words.append(chunks[0])
    logging.info("name={} word={}".format(name,words[:200]))
    return TaggedDocument(words=words, tags=[name])

if __name__ == '__main__':
    print('文字列入力:')
    search_str = input()
    words = split_into_words(search_str).words
    search_similar_texts(words)
    search_similar_words(words)
