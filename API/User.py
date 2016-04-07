# -*- coding: utf-8 -*-
from flask_restful import Resource, fields, marshal
from flask import request, jsonify
from model import User, OrderInfo, OrderComment
from app import db

login_fields = {
    'id': fields.Integer,
    'mobile': fields.String,
    'username': fields.String,
    'type': fields.Integer,
    'password': fields.String,
    'gender': fields.Integer,
    'brief': fields.String,
    'address': fields.String
}

userInfo_fields = {
    'mobile': fields.String,
    'username': fields.String,
    'type': fields.Integer,
    'gender': fields.Integer,
    'brief': fields.String,
    'bonus': fields.Float,
    'orderNum': fields.Integer
}

client_orderComment_fields = {
    'client_comment': fields.String,
    'client_comment_ts': fields.String,
    'courier_user_id': fields.Integer
}

courier_orderComment_fields = {
    'courier_comment': fields.String,
    'courier_comment_ts': fields.String,
    'client_user_id': fields.Integer
}

orderNum_rank_fields = {
    'username': fields.String,
    'gender': fields.Integer,
    'orderNum': fields.Integer
}

bonus_rank_fields = {
    'username': fields.String,
    'gender': fields.Integer,
    'bonus': fields.Float
}


class Login(Resource):
    def post(self):
        data = request.get_json(force=True)
        mobile = data['mobile']
        psw = data['password']
        if mobile and psw:
            user = User.query.filter_by(mobile=mobile).first()
            if not user:
                return jsonify(code='NACK', message='该手机号未注册!')
            else:
                if psw != user.password:
                    return jsonify(code='NACK', message='密码错误,请重新输入!')
                else:
                    return {'code': 'ACK', 'data': marshal(user, login_fields)}


class CheckMobile(Resource):
    def post(self):
        data = request.get_json(force=True)
        mobile = data['mobile']
        flag = data['isChangePwd']  # true-忘记密码验证 false-注册手机验证
        if mobile:
            user = User.query.filter_by(mobile=mobile).first()
            if user:  # 用户存在数据库
                if flag:  # 忘记密码
                    return jsonify(code='ACK', message='验证码正发送到你的手机,请注意查收!')
                else:  # 注册
                    return jsonify(code='NACK', message='该手机号已注册!')
            else:  # 用户不存在数据库
                if flag:
                    return jsonify(code='NACK', message='该手机号未注册!')
                else:
                    return jsonify(code='ACK', message='验证码正发送到你的手机,请注意查收!')


class Register(Resource):
    def post(self):
        data = request.get_json(force=True)
        user = User(data)
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify(code='ACK', message='注册成功,正在跳转登录页!')
        except Exception as e:
            db.session.rollback()
            return jsonify(code='NACK', message='注册失败,请重新注册')


class ChangePwd(Resource):
    def post(self):
        data = request.get_json(force=True)
        mobile = data['mobile']
        pwd = data['password']
        if mobile and pwd:
            user = User.query.filter_by(mobile=mobile).first()
            if not user:
                return jsonify(code='NACK', message='该手机号未注册!')
            if pwd != user.password:
                user.password = pwd
                db.session.commit()
            return jsonify(code='ACK', message='密码修改成功,请重新登录')


class AveScore(Resource):
    def post(self):
        data = request.get_json(force=True)
        userId = data['userId']
        userType = data['userType']
        if userType == 0:  # 获取买家的平均分
            orderInfos = OrderInfo.query.filter_by(client_user_id=userId, is_courier_commented=1).all()
            if orderInfos:  # 有卖家评价过
                count = len(orderInfos)
                score = 0
                for orderInfo in orderInfos:
                    orderComment = orderInfo.orderComment
                    score += orderComment.client_score
                ackScore = (score + 0.0) / count
                return jsonify(code='ACK', message='获取用户平均分成功', data=round(ackScore, 2))
            else:
                return jsonify(code='NACK', message='该买家还未收到评分')

        if userType == 1:
            orderInfos = OrderInfo.query.filter_by(courier_user_id=userId, is_client_commented=1).all()
            if orderInfos:  # 有买家评价过
                count = len(orderInfos)
                score = 0
                for orderInfo in orderInfos:
                    orderComment = orderInfo.orderComment
                    score += orderComment.courier_score
                ackScore = (score + 0.0) / count
                return jsonify(code='ACK', message='获取用户平均分成功', data=round(ackScore, 2))
            else:
                return jsonify(code='NACK', message='该送客还未收到评分')


class UserInfo(Resource):
    def post(self):
        data = request.get_json(force=True)
        userId = data['userId']
        user = User.query.filter_by(id=userId).first()
        if user:
            return jsonify(code='ACK', message='获取用户信息成功', data=marshal(user, userInfo_fields))
        else:
            return jsonify(code='NACK', message='该用户不存在')


class Comments(Resource):
    def post(self):
        data = request.get_json(force=True)
        userId = data['userId']  # 对方id
        userType = data['type']  # 对方type
        number = data.get('number')
        if userType == 0:  # 卖家查看买家的评论
            if number:
                OrderComments = OrderComment.query.filter_by(client_user_id=userId).order_by(
                    OrderComment.client_comment_ts.desc()).limit(number).all()
            else:
                OrderComments = OrderComment.query.filter_by(client_user_id=userId).order_by(
                    OrderComment.client_comment_ts.desc()).all()
            if OrderComments:
                return jsonify(code='ACK', message='获取买家信息成功', data=marshal(OrderComments, client_orderComment_fields))
            else:
                return jsonify(code='NACK', message='改买家暂未收到评论')
        if userType == 1:  # 买家查看卖家的评论
            if number:
                OrderComments = OrderComment.query.filter_by(courier_user_id=userId).order_by(
                    OrderComment.courier_user_id.desc()).limit(number).all()
            else:
                OrderComments = OrderComment.query.filter_by(courier_user_id=userId).order_by(
                    OrderComment.courier_user_id.desc()).all()
            if OrderComments:
                return jsonify(code='ACK', message='获取卖家信息成功', data=marshal(OrderComments, courier_orderComment_fields))
            else:
                return jsonify(code='NACK', message='改卖家暂未收到评论')


class OrdersNumRank(Resource):
    def post(self):
        data = request.get_json(force=True)
        number = data.get('number')
        type = data.get('type')
        if number:  # 有数量限制
            users = User.query.filter_by(type=type).order_by(User.orderNum.desc()).limit(number).all()
        else:
            users = User.query.filter_by(type=type).order_by(User.orderNum.desc()).all()
        return jsonify(code='ACK', message='获取订单数榜单成功', data=marshal(users, orderNum_rank_fields))


class BonusRank(Resource):
    def post(self):
        data = request.get_json(force=True)
        number = data.get('number')
        type = data.get('type')
        if number:  # 有数量限制
            users = User.query.filter_by(type=type).order_by(User.bonus.desc()).limit(number).all()
        else:
            users = User.query.filter_by(type=type).order_by(User.bonus.desc()).all()
        return jsonify(code='ACK', message='获取悬赏金榜单成功', data=marshal(users, bonus_rank_fields))
