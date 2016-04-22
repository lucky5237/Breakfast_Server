# -*- coding: utf-8 -*-

from app import api
from API.User import Login, Register, CheckMobile, ChangePwd, AveScore, UserInfo, BonusRank, OrdersNumRank, UserRank, \
    Comments, UploadImage, ModifyProfile
from API.Order import MakeOrder, MyOrderList, Comment, TakeOrder, UpdateStatus, NewestOrder
from API.Food import SalesRank, PriceRank, AllFood

# 用户相关路由
api.add_resource(Login, '/user/login')
api.add_resource(Register, '/user/register')
api.add_resource(CheckMobile, '/user/checkMobile')
api.add_resource(ChangePwd, '/user/changePassword')
api.add_resource(AveScore, '/user/aveScore')
api.add_resource(UserInfo, '/user/userInfo')
api.add_resource(OrdersNumRank, '/user/orderNumRank')
api.add_resource(BonusRank, '/user/bonusRank')
api.add_resource(UserRank, '/user/rank')
api.add_resource(Comments, '/user/commentList')
api.add_resource(UploadImage, '/user/uploadAvatar')
api.add_resource(ModifyProfile, '/user/modifyProfile')

# 订单相关路由
api.add_resource(MakeOrder, '/order/makeOrder')
api.add_resource(MyOrderList, '/order/orderList')
api.add_resource(Comment, '/order/comment')
api.add_resource(TakeOrder, '/order/takeOrder')
api.add_resource(UpdateStatus, '/order/updateStatus')
api.add_resource(NewestOrder, '/order/newestOrder')

# 食物相关路由
api.add_resource(SalesRank, '/food/salesRank')
api.add_resource(PriceRank, '/food/priceRank')
api.add_resource(AllFood, '/food/allFood')
