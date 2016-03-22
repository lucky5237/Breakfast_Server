from flask_restful import Resource
from flask import request
from model import User


class Login(Resource):
    def post(self):
        data = request.get_json(force=True)
        print 1
        mobile = data['mobile']
        print mobile
        psw = data['password']
        print psw
        if mobile and psw:
            user = User.query.filter_by(mobile=mobile).first()
            if not user:
                return {'code': 'NACK', 'message': 'not exist', 'data': 'null'}
            else:
                return {'fuck': 'youmother'}
