# -*- coding: utf-8 -*-
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config')
api = Api(app)
db = SQLAlchemy(app)


class Food(db.Model):
    __tablename__ = 'food'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    place = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255))
    sales = db.Column(db.Integer, default=0, nullable=False)


class OrderComment(db.Model):
    __tablename__ = 'order_comment'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order_info.id'))
    client_score = db.Column(db.Float)
    client_comment = db.Column(db.String(500))
    courier_score = db.Column(db.Float)
    courier_comment = db.Column(db.String(500))
    client_comment_ts = db.Column(db.DateTime)
    courier_comment_ts = db.Column(db.DateTime)

    def __init__(self, order_id, client_score=None, client_comment=None, courier_score=None, courier_comment=None,
                 client_comment_ts=None,
                 courier_comment_ts=None):
        self.order_id = order_id
        self.client_score = client_score
        self.client_comment = client_comment
        self.courier_score = courier_score
        self.courier_comment = courier_comment
        self.client_comment_ts = client_comment_ts
        self.courier_comment_ts = courier_comment_ts


class OrderDetail(db.Model):
    __tablename__ = 'order_detail'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order_info.id'))
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    food = db.relationship('Food',uselist=False)

    def __init__(self, data):
        self.food_id = data['foodId']
        self.quantity = data['quantity']


class OrderInfo(db.Model):
    __tablename__ = 'order_info'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(16), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)
    create_ts = db.Column(db.DateTime, nullable=False, default=datetime.now())
    amount = db.Column(db.Float, nullable=False)
    received_ts = db.Column(db.DateTime)
    delivery_ts = db.Column(db.DateTime)
    finish_ts = db.Column(db.DateTime)
    cancel_ts = db.Column(db.DateTime)
    cancel_user_type = db.Column(db.Integer, nullable=True, default=None)
    bonus = db.Column(db.Float, nullable=False)
    is_client_commented = db.Column(db.Integer, default=0)
    is_courier_commented = db.Column(db.Integer, default=0)
    client_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    courier_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    orderdetails = db.relationship('OrderDetail', backref='orderInfo', lazy='select')
    orderComment = db.relationship('OrderComment', backref='orderInfo', uselist=False)

    def __init__(self, data):
        self.order_number = data['orderNumber']
        self.amount = data['amount']
        self.bonus = data['bonus']
        self.client_user_id = data['clientUserId']
        self.orderdetails = data['foodList']


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(11), nullable=False, index=True)
    username = db.Column(db.String(45), nullable=False, index=True)
    type = db.Column(db.Integer, nullable=False, default=0)
    password = db.Column(db.String(45), nullable=False)
    gender = db.Column(db.Integer, default=1)
    brief = db.Column(db.String(255))
    create_ts = db.Column(db.DateTime, nullable=False, default=datetime.now())
    address = db.Column(db.String(50))

    def __init__(self, data):
        self.mobile = data['mobile']
        self.password = data['password']
        self.gender = data['gender']
        self.type = data['type']
        self.username = data['username']
        self.address = data['address']


if __name__ == '__main__':
    db.create_all()
