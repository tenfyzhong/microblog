#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from config import basedir
import logging


app = Flask(__name__)
app.config.from_object('config')
handler = logging.FileHandler('flask.log')
# handler.setLevel(logging.DEBUG)
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
)
handler.setFormatter(logging_format)
app.logger.addHandler(handler)
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


from app import views, models
