# -*- coding: utf-8 -*-
from flask_restful import Resource, fields, marshal
from flask import request, jsonify
from model import Food
from app import db

place_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'orderNum': fields.Integer

}
ack_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'price': fields.Float,
    'place': fields.Nested(place_fields),
    'image': fields.String,
    'sales': fields.Integer,
    'createTs': fields.String(attribute='create_ts')
}


class SalesRank(Resource):  # 食品销量榜
    def post(self):
        data = request.get_json(force=True)
        number = data.get('number')
        isAsc = data.get('isAsc')
        if number:
            if isAsc:
                foods = Food.query.order_by(Food.sales).limit(number).all()
            else:
                foods = Food.query.order_by(Food.sales.desc()).limit(number).all()
        else:
            if isAsc:
                foods = Food.query.order_by(Food.sales).all()
            else:
                foods = Food.query.order_by(Food.sales.desc()).all()
        return jsonify(code='ACK', message='获取销量榜成功', data=marshal(foods, ack_fields))


class PriceRank(Resource):  # 食品价格榜
    def post(self):
        data = request.get_json(force=True)
        number = data.get('number')
        isAsc = data.get('isAsc')
        if number:
            if isAsc:
                foods = Food.query.order_by(Food.price).limit(number).all()
            else:
                foods = Food.query.order_by(Food.price.desc()).limit(number).all()
        else:
            if isAsc:
                foods = Food.query.order_by(Food.price).all()
            else:
                foods = Food.query.order_by(Food.price.desc()).all()
        return jsonify(code='ACK', message='获取价格榜成功', data=marshal(foods, ack_fields))


class AllFood(Resource):
    def post(self):
        data = request.get_json(force=True)
        number = data.get('number')
        placeId = data.get('placeId')
        flag = data.get('flag')  # 0-销量 1-时间

        if number:
            if flag == 0:
                foods = Food.query.filter_by(placeId=placeId).order_by(Food.sales.desc()).limit(number).all()
            if flag == 1:
                foods = Food.query.filter_by(placeId=placeId).order_by(Food.create_ts.desc()).limit(number).all()
        else:
            if flag == 0:
                foods = Food.query.filter_by(placeId=placeId).order_by(Food.sales.desc()).all()
            else:
                foods = Food.query.filter_by(placeId=placeId).order_by(Food.create_ts.desc()).all()
        return jsonify(code='ACK', message='获取食品列表成功', data=marshal(foods, ack_fields))
