#!/usr/bin/python
# -*- coding: UTF-8 -*-

# __author__ == 'jianlu'

from app import api, app, db


@app.route('/')
def hellp():
    return 'hello'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
