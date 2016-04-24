# -*- coding: utf-8 -*-
from flask_restful import Resource, fields, marshal
from flask import request, jsonify
from model import User, OrderInfo, OrderComment
from app import db
import os

login_fields = {
    'id': fields.Integer,
    'mobile': fields.String,
    'username': fields.String,
    'type': fields.Integer,
    'password': fields.String,
    'gender': fields.Integer,
    'brief': fields.String,
    'address': fields.String,
    'bonus': fields.Float,
    'orderNum': fields.Integer
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
    'orderId': fields.Integer(attribute='order_id'),
    'clientComment': fields.String(attribute='client_comment'),
    'clientCommentTs': fields.String(attribute='client_comment_ts'),
    'courierUserId': fields.Integer(attribute='courier_user_id'),
    'courierUserName': fields.String(attribute='courier_user_name'),
    'clientScore': fields.Float(attribute='client_score')
}

courier_orderComment_fields = {
    'orderId': fields.Integer(attribute='order_id'),
    'courierComment': fields.String(attribute='courier_comment'),
    'courierCommentTs': fields.String(attribute='courier_comment_ts'),
    'clientUserId': fields.Integer(attribute='client_user_id'),
    'clientUserName': fields.String(attribute='client_user_name'),
    'courierScore': fields.Float(attribute='courier_score')
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

rank_fields = {
    'username': fields.String,
    'gender': fields.Integer,
    'bonus': fields.Float,
    'orderNum': fields.Integer
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
        userName = data['username']
        if User.query.filter_by(username=userName).all():
            return jsonify(code='NACK', message='该用户名已注册,请更换用户名')
        else:
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
        oldPwd = data['oldPassword']
        if mobile and pwd:
            user = User.query.filter_by(mobile=mobile).first()
            if not user:
                return jsonify(code='NACK', message='该手机号未注册!')
            if oldPwd:
                if oldPwd != user.password:
                    return jsonify(code='NACK', message='旧密码不正确!')
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


# class UserInfo(Resource):
#     def post(self):
#         data = request.get_json(force=True)
#         userId = data['userId']
#         userType = data['userType']
#         number = data.get('number')
#         orderComments = []
#         score = 0
#         user = User.query.filter_by(id=userId).first()
#         if user:
#             if userType == 0:  # 卖家查看买家的个人详情页
#                 orderInfos = OrderInfo.query.filter_by(client_user_id=userId, is_courier_commented=1).all()
#                 if orderInfos:  # 有卖家评价过
#                     count = len(orderInfos)
#
#                     for orderInfo in orderInfos:
#                         orderComment = orderInfo.orderComment
#                         score += orderComment.client_score
#                     ackScore = (score + 0.0) / count
#                     if number:
#                         orderComments = OrderComment.query.filter(OrderComment.client_comment != None,
#                                                                   OrderComment.client_user_id == userId).order_by(
#                             OrderComment.client_comment_ts.desc()).limit(number).all()
#                     else:
#                         orderComments = OrderComment.query.filter(OrderComment.client_comment != None,
#                                                                   OrderComment.client_user_id == userId).order_by(
#                             OrderComment.client_comment_ts.desc()).all()
#             if userType == 1:  # 买家查看卖家的评论
#
#                 orderInfos = OrderInfo.query.filter_by(courier_user_id=userId, is_client_commented=1).all()
#                 if orderInfos:  # 有买家评价过
#                     count = len(orderInfos)
#                     score = 0
#                     for orderInfo in orderInfos:
#                         orderComment = orderInfo.orderComment
#                         score += orderComment.courier_score
#                     ackScore = (score + 0.0) / count
#                     if number:
#                         orderComments = OrderComment.query.filter(OrderComment.courier_comment != None,
#                                                                   OrderComment.courier_user_id == userId).order_by(
#                             OrderComment.courier_user_id.desc()).limit(number).all()
#                     else:
#                         orderComments = OrderComment.query.filter(OrderComment.courier_comment != None,
#                                                                   OrderComment.courier_user_id == userId).order_by(
#                             OrderComment.courier_user_id.desc()).all()
#             return jsonify(code='ACK', message='获取用户信息成功',
#                            data=marshal(user, userInfo_fields) + marshal(orderComments,
#                                                                          client_orderComment_fields))
#         else:
#             return jsonify(code='NACK', message='该用户不存在')


class UserInfo(Resource):
    def post(self):
        userId = request.get_json(force=True)
        user = User.query.filter_by(id=userId).first()
        if user:
            return jsonify(code='ACK', message='获取用户信息成功', data=marshal(user, userInfo_fields))
        else:
            return jsonify(code='NACK', message='该用户不存在')


class Comments(Resource):
    def post(self):
        data = request.get_json(force=True)
        userId = data['userId']  # 对方id
        userType = data['userType']  # 对方type
        number = data.get('number')
        if userType == 0:  # 卖家查看买家的评论
            if number:
                OrderComments = OrderComment.query.filter(OrderComment.client_comment != None,
                                                          OrderComment.client_user_id == userId).order_by(
                    OrderComment.client_comment_ts.desc()).limit(number).all()
            else:
                OrderComments = OrderComment.query.filter(OrderComment.client_comment != None,
                                                          OrderComment.client_user_id == userId).order_by(
                    OrderComment.client_comment_ts.desc()).all()
            if OrderComments:
                return jsonify(code='ACK', message='获取买家信息成功', data=marshal(OrderComments, client_orderComment_fields))
            else:
                return jsonify(code='NACK', message='该买家暂未收到评论')
        if userType == 1:  # 买家查看卖家的评论
            if number:
                OrderComments = OrderComment.query.filter(OrderComment.courier_comment != None,
                                                          OrderComment.courier_user_id == userId).order_by(
                    OrderComment.courier_comment_ts.desc()).limit(number).all()
            else:
                OrderComments = OrderComment.query.filter(OrderComment.courier_comment != None,
                                                          OrderComment.courier_user_id == userId).order_by(
                    OrderComment.courier_comment_ts.desc()).all()
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


class UserRank(Resource):
    def post(self):
        data = request.get_json(force=True)
        number = data.get('number')  # 返回的数量 默认10条
        type = data.get('type')  # 用户类型
        flag = data.get('flag')  # 0-悬赏金 1-订单数
        if number:  # 有数量限制
            if flag == 0:  # 按照悬赏金排行
                users = User.query.filter_by(type=type).order_by(User.bonus.desc()).limit(number).all()
            if flag == 1:  # 按照订单数排行
                users = User.query.filter_by(type=type).order_by(User.orderNum.desc()).limit(number).all()
        else:
            if flag == 0:  # 按照悬赏金排行
                users = User.query.filter_by(type=type).order_by(User.bonus.desc()).all()
            if flag == 1:  # 按照订单数排行
                users = User.query.filter_by(type=type).order_by(User.orderNum.desc()).all()
        return jsonify(code='ACK', message='获取悬赏金榜单成功', data=marshal(users, rank_fields))


class UploadImage(Resource):
    def post(self):
        file = request.files['avatar']
        if file:
            filename = file.filename
            try:
                file.save('static/avatar/' + filename)
                return jsonify(code='ACK', message='头像上传成功')
            except Exception as e:
                return jsonify(code='NACK', message='头像上传失败' + e.message)


class ModifyProfile(Resource):
    def post(self):
        data = request.get_json(force=True)
        id = data['userId']
        gender = data['gender']
        address = data['address']
        user = User.query.filter_by(id=id).first()
        if user:
            try:
                user.address = address
                user.gender = gender
                db.session.add(user)
                db.session.commit()
                return jsonify(code='ACK', message='修改成功')
            except Exception as e:
                db.session.rollback()
                return jsonify(code='NACK', message='服务器发生异常')
