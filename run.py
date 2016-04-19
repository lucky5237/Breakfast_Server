#!/usr/bin/python
# -*- coding: UTF-8 -*-

# __author__ == 'jianlu'

from app import app
from flask import url_for
import os
import views

if __name__ == '__main__':
    app.run(host='0.0.0.0')
