#!/usr/bin/python
# -*- coding: UTF-8 -*-

#__author__ == 'jianlu'

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from API.User import Login


app = Flask(__name__)
app.config.from_object('config')
api = Api(app)
db = SQLAlchemy(app)
api.add_resource(Login,'/user')
