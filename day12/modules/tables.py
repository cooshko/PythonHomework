#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean

engine = create_engine("mysql+pymysql://root:24559982@192.168.5.138:3306/baoleiji?charset=utf8", echo=False)
Base = declarative_base()


class User(Base):
    # 堡垒机用户表
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    enable = Column(Boolean, default=True)
    group = relationship("Group", backref="user")


class Group(Base):
    # 堡垒机用户组表
    __tablename__ = "group"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255))


class User2Group(Base):
    # 用户关联组表，多对多的关系
    __tablename__ = "user2group"
    uid = Column(Integer, ForeignKey("user.id"), primary_key=True)
    gid = Column(Integer, ForeignKey("group.id"), primary_key=True)
    __table_args__ = (UniqueConstraint("uid", "gid", name="_u_g_uc"),)


class Host(Base):
    # 主机表
    __tablename__ = "host"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    ip = Column(String(15), nullable=False)
    port = Column(Integer, default=22)
    auth_use_password = Column(Boolean, nullable=False)
    auth_user = Column(String(64))
    auth_password = Column(String(64))
    auth_key = Column(String(255))


class HostGroup(Base):
    # 主机组表
    __tablename__ = "host_group"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255))


class Host2Group(Base):
    # 主机关联主机组
    __tablename__ = "host2group"
    hid = Column(Integer, ForeignKey("host.id"), primary_key=True)
    hgid = Column(Integer, ForeignKey("host_group.id"), primary_key=True)
    __table_args__ = (UniqueConstraint("hid", "hgid", name="_h_hg_uc"),)


class User2Host(Base):
    # 堡垒机用户关联主机
    __tablename__ = "user2host"
    uid = Column(Integer, ForeignKey("user.id"), nullable=False)
    hid = Column(Integer, ForeignKey("host.id"), nullable=False)
    __table_args__ = (UniqueConstraint("hid", "uid", name="_u_h_uc"),)

if __name__ == '__main__':
    Base.metadata.create_all(engine)

