#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime, configparser
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.types import Boolean

cp = configparser.ConfigParser()
cp.read(r"../conf/baoleiji.conf")
db_type = cp['db']['db_type']
db_connector = cp['db']['connector']
db_ip = cp['db']['ip']
db_port = cp['db']['port']
db_user = cp['db']['username']
db_pass = cp['db']['password']
db_name = cp['db']['db_name']
db_charset = cp['db']['charset']
conn_str = "{db_type:s}+{connector:s}://{db_user:s}:{db_pass:s}@{db_ip:s}:{db_port:s}/{db_name:s}?charset={charset:s}"\
    .format(connector=db_connector,
            db_type=db_type,
            db_user=db_user,
            db_pass=db_pass,
            db_ip=db_ip,
            db_port=db_port,
            db_name=db_name,
            charset=db_charset
            )
engine = create_engine(conn_str, echo=False)
Base = declarative_base()
session = sessionmaker(bind=engine)()


class User2Group(Base):
    # 用户关联组表，多对多的关系
    __tablename__ = "user2group"
    uid = Column(Integer, ForeignKey("user.id"), primary_key=True)
    gid = Column(Integer, ForeignKey("user_group.id"), primary_key=True)
    __table_args__ = (UniqueConstraint("uid", "gid", name="_u_g_uc"),)
    user = relationship("User", backref="user2group")
    user_group = relationship("UserGroup", backref="user2group")


class User(Base):
    # 堡垒机用户表
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    enable = Column(Boolean, default=True)
    user_group = relationship("UserGroup", secondary=User2Group.__table__, back_populates="user")


class UserGroup(Base):
    # 堡垒机用户组表
    __tablename__ = "user_group"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255))
    user = relationship("User", secondary=User2Group.__table__, back_populates="user_group")


class Host2HostGroup(Base):
    # 主机关联主机组
    __tablename__ = "host2group"
    hid = Column(Integer, ForeignKey("host.id"), primary_key=True)
    hgid = Column(Integer, ForeignKey("host_group.id"), primary_key=True)
    __table_args__ = (UniqueConstraint("hid", "hgid", name="_h_hg_uc"),)
    host = relationship("Host", backref="host2group")
    host_group = relationship("HostGroup", backref="host2group")


class Host2HostUser(Base):
    __tablename__ = "host2host_user"
    hid = Column(Integer, ForeignKey("host.id"), primary_key=True)
    huid = Column(Integer, ForeignKey("host_user.id"), primary_key=True)
    __table_args__ = (UniqueConstraint("hid", "huid", name="_h_hu_uc"),)
    host = relationship("Host", backref="host2host_user")
    host_user = relationship("HostUser", backref="host2host_user")


class Host(Base):
    # 主机表
    __tablename__ = "host"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    ip = Column(String(15), nullable=False)
    port = Column(Integer, default=22)
    host_user = relationship("HostUser", secondary=Host2HostUser.__table__, back_populates="host")
    host_group = relationship("HostGroup", secondary=Host2HostGroup.__table__, back_populates="host")


class HostGroup(Base):
    # 主机组表
    __tablename__ = "host_group"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255))
    host = relationship("Host", secondary=Host2HostGroup.__table__, back_populates="host_group")


class HostUser(Base):
    # 主机上的用户
    # 这个表不能建立唯一约束，场景是有两个组的机器都是相同的认证信息，
    # 但后来要分开，那么在最开始的时候，应该分开来存两份一模一样的认证信息
    __tablename__ = "host_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    using_key = Column(Boolean, default=False)
    auth_user = Column(String(64), nullable=False)
    auth_pass = Column(String(64))
    auth_key = Column(String(255))
    host = relationship("Host", secondary=Host2HostUser.__table__, back_populates="host_user")


class User2Host2HostUser(Base):
    # 堡垒机用户关联到主机和主机用户
    __tablename__ = "user2host2host_user"
    uid = Column(Integer, ForeignKey("user.id"), primary_key=True)
    hid = Column(Integer, ForeignKey("host.id"), primary_key=True)
    hgid = Column(Integer, ForeignKey("host_group.id"), primary_key=True)
    huid = Column(Integer, ForeignKey("host_user.id"), primary_key=True)
    __table_args__ = ((UniqueConstraint("uid", "hid", "hgid", "huid", name="_u_h_hg_hu_uc")),)


if __name__ == '__main__':
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

