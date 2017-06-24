#!/home/ubuntu/anaconda3/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import MeCab
import collections
from gensim import models
from gensim.models.doc2vec import LabeledSentence,TaggedDocument

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

INPUT_DOC_DIR = './aozora2/'
OUTPUT_MODEL = 'doc2vec.model.souseki'
PASSING_PRECISION = 93

# 全てのファイルのリストを取得
def get_all_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

# ファイルから文章を返す
def read_document(path):
    with open(path, 'r', encoding='sjis', errors='ignore') as f:
        return f.read()

# 青空文庫ファイルから作品部分のみ抜き出す
def trim_doc(doc):
    lines = doc.splitlines()
    valid_lines = []
    is_valid = False
    horizontal_rule_cnt = 0
    break_cnt = 0
    for line in lines:
        if horizontal_rule_cnt < 2 and '-----' in line:
            horizontal_rule_cnt += 1
            is_valid = horizontal_rule_cnt == 2
            continue
        if not(is_valid):
            continue
        if line == '':
            break_cnt += 1
            is_valid = break_cnt != 3
            continue
        break_cnt = 0
        valid_lines.append(line)
    return ''.join(valid_lines)

# 文章から単語に分解して返す
def split_into_words(doc, name=''):
    mecab = MeCab.Tagger("-Ochasen")
    valid_doc = trim_doc(doc)
    lines = mecab.parse(doc).splitlines()
    words = []
    for line in lines:
        chunks = line.split('\t')
        if len(chunks) > 3 and (chunks[3].startswith('動詞') or chunks[3].startswith('形容詞') or (chunks[3].startswith('名詞') and not chunks[3].startswith('名詞-数'))):
            words.append(chunks[0])
    #logging.info("name={} word={}".format(name,words[:200]))
    return TaggedDocument(words=words, tags=[name])

# ファイルから単語のリストを取得
def corpus_to_sentences(corpus):
    docs = [read_document(x) for x in corpus]
    for idx, (doc, name) in enumerate(zip(docs, corpus)):
        #logging.info("name={} doc={} docsize={}".format(name,doc[:200],len(doc)))
        sys.stdout.write('\r前処理中 {} / {}'.format(idx, len(corpus)))
        yield split_into_words(doc, name)

# 学習
def train(sentences):
    model = models.Doc2Vec(size=400, alpha=0.0015, sample=1e-4, min_count=1, workers=4)
    model.build_vocab(sentences)
    for x in range(30):
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

if __name__ == '__main__':
    corpus = list(get_all_files(INPUT_DOC_DIR))
    sentences = list(corpus_to_sentences(corpus))
    print()
    model = train(sentences)
    model.save(OUTPUT_MODEL)
