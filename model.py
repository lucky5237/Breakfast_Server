# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Food(Base):
    __tablename__ = 'food'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(4, 1), nullable=False)
    place = Column(String(100), nullable=False)
    image = Column(String(255))


class OrderComment(Base):
    __tablename__ = 'order_comment'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    client_score = Column(Numeric(2, 1))
    client_comment = Column(String(500))
    courier_score = Column(Numeric(2, 1))
    courier_comment = Column(String(500))
    client_comment_ts = Column(DateTime)
    courier_comment_ts = Column(DateTime)


class OrderDetail(Base):
    __tablename__ = 'order_detail'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey(u'order_info.id'), nullable=False, index=True)
    food_id = Column(ForeignKey(u'food.id'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, server_default=text("'1'"))

    food = relationship(u'Food')
    order = relationship(u'OrderInfo')


class OrderInfo(Base):
    __tablename__ = 'order_info'

    id = Column(Integer, primary_key=True)
    order_number = Column(String(16), nullable=False)
    client_user_id = Column(ForeignKey(u'user.id'), nullable=False, index=True)
    courier_user_id = Column(ForeignKey(u'user.id'), index=True)
    status = Column(String(15), nullable=False)
    create_ts = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    amout = Column(Numeric(4, 1), nullable=False)
    received_ts = Column(DateTime)
    bonus = Column(Numeric(4, 2), nullable=False)
    is_client_commented = Column(Integer, server_default=text("'0'"))
    is_courier_commented = Column(Integer, server_default=text("'0'"))

    client_user = relationship(u'User', primaryjoin='OrderInfo.client_user_id == User.id')
    courier_user = relationship(u'User', primaryjoin='OrderInfo.courier_user_id == User.id')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    mobile = Column(String(11), nullable=False, index=True)
    username = Column(String(45), nullable=False, index=True)
    type = Column(Integer, nullable=False, server_default=text("'0'"))
    password = Column(String(45), nullable=False)
    gender = Column(Integer, server_default=text("'1'"))
    brief = Column(String(255))
    captcha = Column(String(6))
    create_ts = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    update_ts = Column(DateTime)
    address = Column(String(50))
