#!/usr/bin/env python
# -*- coding:utf-8 -*-

import MeCab
from flask import Flask,g,render_template,request,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import TextField,SubmitField
from gensim import models
from gensim.models.doc2vec import TaggedDocument
from flask_wtf.csrf import CSRFProtect
app = Flask(__name__)
app.secret_key = 'myverylongsecretkey'
csrf = CSRFProtect()
csrf.init_app(app)
MODEL_PATH="model/doc2vec.model.laws5"
model = models.Doc2Vec.load(MODEL_PATH)

class InputArea(FlaskForm):
    word = TextField("input law word")
    submit = SubmitField("Send")   

@app.before_request
def before_request():
    g.model=model
    app.logger.info("g.model={}".format(g.model))

@app.route("/")
def index():
    form=InputArea(request.form)
    return render_template('index.html',form=form)

def main():
    app.run(host='0.0.0.0',debug=True)
if __name__=='__main__':main()
