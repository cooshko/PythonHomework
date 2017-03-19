#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,relationship
from conf import config

# 需要创建一个engine
engine = create_engine(config.db_parameters[config.db_type])
# 创建一个基类
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    uid = Column(Integer, primary_key=True, autoincrement=True)
    password = Column(String(64), nullable=False, )
    name = Column(String(64), nullable=False)
    nickname = Column(String(64), nullable=True)
    head = Column(Text, nullable=True)
    create_on = Column(DateTime(True), nullable=False, default=datetime.datetime.now)
    chatrooms = relationship("Chatroom", secondary="chatroom_users", backref="user")


class Chatroom(Base):
    __tablename__ = "chatroom"
    rid = Column(Integer, primary_key=True, autoincrement=True)
    room_type = Column(Integer)
    title = Column(String, nullable=False)
    owner = Column(Integer, ForeignKey("user.uid"), nullable=False)
    create_on = Column(DateTime(True), nullable=False, default=datetime.datetime.now)
    users = relationship("User", secondary="chatroom_users", backref="chatroom")
    managers = relationship("User", secondary="charoom_managers")


class ChatroomUsers(Base):
    # 聊天室与用户的多对多关联表
    __tablename__ = "chatroom_users"
    # id = Column(Integer, primary_key=True, autoincrement=True)
    rid = Column(Integer, ForeignKey("chatroom.rid"), nullable=False, primary_key=True)
    uid = Column(Integer, ForeignKey("user.uid"), nullable=False, primary_key=True)
    speakable = Column(Boolean, default=True)
    users = relationship(User)
    chatrooms = relationship(Chatroom)
    __table_args__ = (UniqueConstraint("uid", "rid", name="_u_r_uc"),)  # 用户和聊天室联合唯一


class ChatroomManagers(Base):
    __tablename__ = "charoom_managers"
    rid = Column(Integer, ForeignKey("chatroom.rid"), nullable=False, primary_key=True)
    uid = Column(Integer, ForeignKey("user.uid"), nullable=False, primary_key=True)
    __table_args__ = (UniqueConstraint("uid", "rid", name="_u_r_uc"),)  # 用户和聊天室联合唯一


class Friends(Base):
    __tablename__ = "friends"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, nullable=False)
    fid = Column(Integer, nullable=False)
    # user = relationship(User, backref="friends")
    __table_args__ = (UniqueConstraint("uid", "fid", name="_u_f_uc"),)

if __name__ == '__main__':
    # 创建这些表。只要调用Base的create_all方法，就会自动去检索所有派生类并创建这些表
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

