#!/usr/bin/env python
# -*- coding:utf-8 -*-

import MeCab
from flask import Flask,g,render_template,request,redirect,url_for,flash
from flask_wtf import FlaskForm
from wtforms import TextField,SubmitField
from gensim import models
from gensim.models.doc2vec import TaggedDocument
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient
import random
app = Flask(__name__)
app.secret_key = 'myverylongsecretkey'
csrf = CSRFProtect()
csrf.init_app(app)
laws_model=['laws','laws2','laws3','laws4','laws5']
#laws_model=['laws','laws2']
cat_model=['laws7']
def init_models(src_path):
    mdict={}
    for s in src_path:
        mpath="model/doc2vec.model.{}".format(s)
        mdict[s]=models.Doc2Vec.load(mpath)
    return mdict
laws_dict=init_models(laws_model)
cat_dict=init_models(cat_model)

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

def init_mongo():
    mp=connect_mongo()
    app.logger.info(mp)
    pipeline=[{"$group":{"_id":"$cat"}}]
    cats=set()
    for c in mp.base.aggregate(pipeline):
        cats.add(c["_id"])
    return mp,cats

mp,cats=init_mongo()

class InputArea(FlaskForm):
    word = TextField("input law positive word")
    neg_word = TextField("input law negative word")
    submit = SubmitField("Send")

def split_into_words(string):
    mecab = MeCab.Tagger("-Ochasen")
    lines = mecab.parse(string).splitlines()
    words = []
    for line in lines:
        chunks = line.split('\t')
        if len(chunks) > 3 and (chunks[3].startswith('名詞') and not chunks[3].startswith('名詞-数')):
            words.append(chunks[0])
            app.logger.info("word={}".format(words[:200]))
    return words

@app.before_request
def before_request():
    g.laws_dict=laws_dict
    g.cat_dict=cat_dict
    g.mp=mp
    pipeline=[{"$sample":{"size":20}}]
    g.law_sample=mp.base.aggregate(pipeline)
    g.cats=cats
    #app.logger.info("g.laws_model={}".format(g.laws_dict))
    #app.logger.info("g.cat_model={}".format(g.cat_dict))
    #app.logger.info("g.mp={}".format(g.mp))
    #app.logger.info("g.cats={}".format(g.cats))
    #app.logger.info("g.law_sampling={}".format(g.law_sample))
    
@app.route("/search/",methods=["GET","POST"])
@app.route("/search",methods=["GET","POST"])
def search():
    form=InputArea(request.form)
    rdict={}
    if request.method=='POST':
        word=request.form['word']
        words=split_into_words(word)
        neg_word=request.form['neg_word']
        neg_words=split_into_words(neg_word)
        app.logger.info("word={} neg_words={}".format(words,neg_words))
        for k,model in g.laws_dict.items():
            try:
                r=model.most_similar(positive=words, negative=neg_words,topn=20)
                rdict[k]=r
            except KeyError as err:
                app.logger.error(err)
                flash("err={}".format(err))
                return redirect(url_for('search'))
    return render_template('search.html',form=form,rdict=rdict)

@app.route("/",methods=['GET'])
def index():
    form=InputArea(request.form)
    catdict={}
    rdict={}
    lawdict={}
    for l in g.law_sample:
        title=l['title']
        lawdict[title]={}
        for k,model in g.laws_dict.items():
            try:
                r=model.docvecs.most_similar(title)
                lawdict[title][k]=r
            except KeyError as err:
                app.logger.error(err)
                flash("title={} is not not in vocabulary".format(title))
                return redirect(url_for('index',form=form,ridct=rdict,catdict=catdict,lawdict=lawdict))
    for c in random.sample(g.cats,10):
        catdict[c]=g.cat_dict['laws7'].docvecs.most_similar(c)
    return render_template('index.html',form=form,catdict=catdict,rdict=rdict,lawdict=lawdict)
def main():
    app.run(host='0.0.0.0',debug=True)
if __name__=='__main__':main()
