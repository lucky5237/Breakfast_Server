# -*- coding: utf-8 -*-
from flask_restful import Resource, fields, marshal
from flask import request, jsonify
from model import OrderInfo, OrderComment, OrderDetail
from app import db
from datetime import datetime

food_fields = {
    'name': fields.String,
    'price': fields.Float,
    'place': fields.String,
    'image': fields.String,
    'sales': fields.Integer
}

orderDetail_fields = {
    'quantity': fields.Integer,
    'food': fields.Nested(food_fields)
}

ack_fields = {
    'id': fields.Integer,
    'order_number': fields.String,
    'status': fields.Integer,
    'create_ts': fields.String,
    'amount': fields.Float,
    'bonus': fields.Float,
    'received_ts': fields.String,
    'delivery_ts': fields.String,
    'finish_ts': fields.String,
    'cancel_ts': fields.String,
    'cancel_user_type': fields.Integer,
    'orderdetails': fields.Nested(orderDetail_fields),
    'is_client_commented': fields.Integer,
    'is_courier_commented': fields.Integer,
    'client_user_id': fields.Integer,
    'courier_user_id': fields.Integer
}


class MakeOrder(Resource):  # 创建订单
    def post(self):
        foodList = []
        data = request.get_json(force=True)
        for item in data['orderDetails']:
            orderDetail = OrderDetail(item)
            foodList.append(orderDetail)
            db.session.add(orderDetail)
        orderinfo = OrderInfo(data, foodList)
        try:
            db.session.add(orderinfo)
            db.session.commit()
            return jsonify(code='ACK', message='订单创建成功,快去首页看看吧')
        except Exception as e:
            db.session.rollback()
            return jsonify(code='NACK', message='下单失败,请稍后重试' + e.message)


class OrderList(Resource):  # 获取订单列表
    def post(self):
        data = request.get_json(force=True)
        type = data['type']  # 用户类型
        userId = data['userId']  # 用户id
        try:
            if type == 0:  # 下单人
                orders = OrderInfo.query.order_by(OrderInfo.create_ts.desc()).filter_by(client_user_id=userId).all()
            if type == 1:  # 接单人
                orders = OrderInfo.query.order_by(OrderInfo.create_ts.desc()).filter_by(courier_user_id=userId).all()
            return jsonify(code='ACK', message='获取全部订单成功', data=marshal(orders, ack_fields))

        except Exception as e:
            return jsonify(code='NACK', message='获取订单发生异常,请稍后重试')


class Comment(Resource):  # 订单评论
    def post(self):
        data = request.get_json(force=True)
        print data
        type = data['type']  # 用户类型
        score = data['score']  # 用户评分分数
        orderId = data['orderId']  # 订单id
        comment = data['comment']  # 用户评论
        userId = data['userId']  # 用户id
        orderComment = OrderComment.query.filter_by(order_id=orderId).first()
        if orderComment:  # 如果已经存在,更新表数据
            if type == 0:  # 下单人的评论
                orderComment.courier_score = score
                orderComment.courier_comment = comment
                orderComment.courier_comment_ts = datetime.now()
                OrderComment.client_user_id = userId
            if type == 1:
                orderComment.client_score = score
                orderComment.client_comment = comment
                orderComment.client_comment_ts = datetime.now()
                orderComment.courier_user_id = userId
        else:  # 如果双方第一次有人评论则创建数据
            if type == 0:  # 下单人的评论
                mOrderComment = OrderComment(orderId, courier_score=score, courier_comment=comment,
                                             courier_comment_ts=datetime.now(), client_user_id=userId)
            if type == 1:
                mOrderComment = OrderComment(orderId, client_score=score, client_comment=comment,
                                             client_comment_ts=datetime.now(), courier_user_id=userId)
            db.session.add(mOrderComment)

        try:
            db.session.commit()
            orderInfo = OrderInfo.query.filter_by(id=orderId).first()
            if orderInfo:  # 更新orderInfo中是否评论的字段
                if type == 0:
                    orderInfo.is_client_commented = 1
                if type == 1:
                    orderInfo.is_courier_commented = 1
            db.session.commit()
            return jsonify(code='ACK', message='订单评论成功')
        except Exception as e:
            db.session.rollback()
            return jsonify(code='NACK', message='评论失败,请稍后重试' + e.message)


class TakeOrder(Resource):  # 接单
    def post(self):
        data = request.get_json(force=True)
        orderId = data['orderId']
        userId = data['courierUserId']
        orderInfo = OrderInfo.query.filter_by(id=orderId).first()
        if orderInfo:
            if orderInfo.status == 0:
                orderInfo.status = 1
                orderInfo.courier_user_id = userId
                orderInfo.received_ts = datetime.now()
                try:
                    db.session.commit()
                    return jsonify(code='ACK', message='接单成功')
                except Exception:
                    db.session.rollback()
                    return jsonify(code='NACK', message='抢单失败,请重试')
            if orderInfo.status == 1:
                return jsonify(code='NACK', message='手速慢了一点,别人抢先一步了')


class UpdateStatus(Resource):  # 更改订单状态
    def post(self):
        data = request.get_json(force=True)
        status = data['status']
        userType = data['userType']
        orderId = data['orderId']
        orderInfo = OrderInfo.query.filter_by(id=orderId).first()
        if orderInfo:
            if status == 2:  # 卖家开始派送
                orderInfo.delivery_ts = datetime.now()
            if status == 3:  # 买家确认收货
                orderInfo.finish_ts = datetime.now()
                bonus = orderInfo.bonus
                clientUser = orderInfo.clientUser
                courierUser = orderInfo.courierUser
                clientUser.bonus += bonus
                clientUser.orderNum += 1
                courierUser.bonus += bonus
                courierUser.orderNum += 1
                db.session.add(clientUser)
                db.session.add(courierUser)
                orderDetails = orderInfo.orderdetails
                for orderDetail in orderDetails:
                    food = orderDetail.food
                    sales = orderDetail.quantity
                    food.sales += sales
                    db.session.add(food)
            if status == 4:  # 取消订单
                if orderInfo.status == 4:
                    return jsonify(code='NACK', message='订单已被对方取消,请刷新订单')
                else:
                    orderInfo.cancel_ts = datetime.now()
                    orderInfo.cancel_user_type = userType
            orderInfo.status = status
            try:
                db.session.commit()
                return jsonify(code='ACK', message='订单状态更改成功')
            except Exception:
                db.session.rollback()
                return jsonify(code='ACK', message='订单状态更改失败,请稍后再试')
