# -*- coding: utf-8 -*-
from flask_restful import Resource, fields, marshal
from flask import request, jsonify
from model import OrderInfo, OrderComment, OrderDetail
from app import db
from datetime import datetime

place_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'orderNum': fields.Integer

}
food_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'price': fields.Float,
    'place': fields.Nested(place_fields),
    'image': fields.String,
    'sales': fields.Integer,
    'createTs': fields.String(attribute='create_ts')
}

orderDetail_fields = {
    'quantity': fields.Integer,
    'food': fields.Nested(food_fields)
}

user_fields = {
    'id': fields.Integer,
    'mobile': fields.String,
    'username': fields.String,
    'type': fields.Integer,
    'gender': fields.Integer,
    'brief': fields.String,
    'address': fields.String,
    'bonus': fields.Float,
    'orderNum': fields.Integer
}

myOrderList_fields = {
    'id': fields.Integer,
    'order_number': fields.String(attribute='orderNumber'),
    'status': fields.Integer,
    'createTs': fields.String(attribute='create_ts'),
    'amount': fields.Float,
    'bonus': fields.Float,
    'receivedTs': fields.String(attribute='received_ts'),
    'deliveryTs': fields.String(attribute='delivery_ts'),
    'finishTs': fields.String(attribute='finish_ts'),
    'cancelTs': fields.String(attribute='cancel_ts'),
    'cancelUserType': fields.Integer(attribute='cancel_user_type'),
    'orderdetails': fields.Nested(orderDetail_fields),
    'isClientCommented': fields.Integer(attribute='is_client_commented'),
    'isCourierCommented': fields.Integer(attribute='is_courier_commented'),
    'clientUser': fields.Nested(user_fields),
    'courierUser': fields.Nested(user_fields)
}

newestOrder_fields = {
    'id': fields.Integer,
    'order_number': fields.String(attribute='orderNumber'),
    'status': fields.Integer,
    'createTs': fields.String(attribute='create_ts'),
    'amount': fields.Float,
    'bonus': fields.Float,
    'orderdetails': fields.Nested(orderDetail_fields),
    'clientUser': fields.Nested(user_fields)
}


class MakeOrder(Resource):  # 创建订单
    def post(self):
        foodList = []
        data = request.get_json(force=True)
        for item in data['orderDetails']:
            orderDetail = OrderDetail(item)
            foodList.append(orderDetail)
            db.session.add(orderDetail)
        orderinfo = OrderInfo(data, foodList, datetime.now())
        try:
            db.session.add(orderinfo)
            db.session.commit()
            return jsonify(code='ACK', message='订单创建成功,请等候接单')
        except Exception as e:
            db.session.rollback()
            return jsonify(code='NACK', message='下单失败,请稍后重试' + e.message)


class MyOrderList(Resource):  # 获取订单列表
    def post(self):
        data = request.get_json(force=True)
        type = data['userType']  # 用户类型
        userId = data['userId']  # 用户id
        status = data.get('status')
        try:
            if type == 0:  # 下单人
                if status != None:
                    orders = OrderInfo.query.order_by(OrderInfo.create_ts.desc()).filter_by(client_user_id=userId,
                                                                                            status=status).all()
                else:
                    orders = OrderInfo.query.order_by(OrderInfo.create_ts.desc()).filter_by(client_user_id=userId).all()
            if type == 1:  # 接单人
                if status != None:
                    orders = OrderInfo.query.order_by(OrderInfo.create_ts.desc()).filter_by(
                        courier_user_id=userId, status=status).all()
                else:
                    orders = OrderInfo.query.order_by(OrderInfo.create_ts.desc()).filter_by(
                        courier_user_id=userId).all()
            return jsonify(code='ACK', message='获取全部订单成功', data=marshal(orders, myOrderList_fields))

        except Exception as e:
            return jsonify(code='NACK', message='获取订单发生异常,请稍后重试')


class Comment(Resource):  # 订单评论
    def post(self):
        data = request.get_json(force=True)
        type = data['userType']  # 用户类型
        score = data['score']  # 用户评分分数
        orderId = data['orderId']  # 订单id
        comment = data['comment']  # 用户评论
        userId = data['userId']  # 用户id
        userName = data['userName']  # 用户名
        otherUserId = data['theOtherUserId']
        otherUserName = data['theOtherUserName']
        orderComment = OrderComment.query.filter_by(order_id=orderId).first()
        if orderComment:  # 如果已经存在,更新表数据
            if type == 0:  # 下单人的评论
                orderComment.courier_score = score
                orderComment.courier_comment = comment
                orderComment.courier_comment_ts = datetime.now()
            if type == 1:
                orderComment.client_score = score
                orderComment.client_comment = comment
                orderComment.client_comment_ts = datetime.now()

        else:  # 如果双方第一次有人评论则创建数据
            if type == 0:  # 下单人的评论
                mOrderComment = OrderComment(orderId, courier_score=score, courier_comment=comment,
                                             courier_comment_ts=datetime.now(), client_user_id=userId,
                                             client_user_name=userName, courier_user_id=otherUserId,
                                             courier_user_name=otherUserName)
            if type == 1:
                mOrderComment = OrderComment(orderId, client_score=score, client_comment=comment,
                                             client_comment_ts=datetime.now(), courier_user_id=userId,
                                             courier_user_name=userName, client_user_id=otherUserId,
                                             client_user_name=otherUserName)
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


class NewestOrder(Resource):
    def post(self):
        data = request.get_json(force=True)
        number = data.get('number')
        flag = data.get('flag')  # 0-按时间最新排序 1-按悬赏高排序
        if number:
            if flag == 0:
                orders = OrderInfo.query.filter_by(status=0).order_by(OrderInfo.create_ts.desc()).limit(number).all()
            if flag == 1:
                orders = OrderInfo.query.filter_by(status=0).order_by(OrderInfo.bonus.desc()).limit(number).all()
        else:
            if flag == 0:
                orders = OrderInfo.query.filter_by(status=0).order_by(OrderInfo.create_ts.desc()).all()
            if flag == 1:
                orders = OrderInfo.query.filter_by(status=0).order_by(OrderInfo.bonus.desc()).all()
        return jsonify(code='ACK', message='获取最新订单成功', data=marshal(orders, newestOrder_fields))
