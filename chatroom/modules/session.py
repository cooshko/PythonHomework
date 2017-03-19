#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime, uuid, redis, json
from conf import config


class BaseSession(object):
    def __init__(self, handler):
        if handler:
            self.session_id = handler.get_cookie("session_id", None)
            if self.session_id and self.has_session(self.session_id):
                self.session = self.get_session(self.session_id)
            else:
                self.session_id = self.new_session()
                handler.set_cookie("session_id", self.session_id)

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()

    def __getitem__(self, item):
        raise NotImplementedError()

    @staticmethod
    def has_session(session_id):
        raise NotImplementedError()

    @staticmethod
    def get_session(session_id):
        raise NotImplementedError()

    @staticmethod
    def new_session():
        raise NotImplementedError()

    @staticmethod
    def destroy_session(session_id):
        raise NotImplementedError()


class MemorySession(BaseSession):
    table = {}

    def __init__(self, handler):
        super(MemorySession, self).__init__(handler)

    def __getitem__(self, item):
        return self.table[self.session_id][item] if item in self.table[self.session_id] else None

    def __delitem__(self, key):
        if key in self.table:
            del self.table[self.session_id][key]

    def __setitem__(self, key, value):
        self.table[self.session_id][key] = value

    @staticmethod
    def has_session(session_id):
        return session_id in MemorySession.table

    @staticmethod
    def get_session(session_id):
        return MemorySession.table[session_id]

    @staticmethod
    def new_session():
        session_id = str(uuid.uuid4())
        MemorySession.table[session_id] = {}
        return session_id


class RedisSession(BaseSession):
    host = config.redis_session_parameter.get('host')
    port = config.redis_session_parameter.get('port')
    key = config.redis_session_parameter.get('auth_key')
    # 连接redis服务器
    if host and port:
        server = redis.Redis(host=host, port=port, password=key)
    else:
        raise ValueError("Redis的主机或端口参数错误")

    def __init__(self, handler):
        super(RedisSession, self).__init__(handler)
        self.session = self.get_session(self.session_id)

    def __delitem__(self, key):
        if key in self.session:
            del self.session[key]
            self.save_session()

    def __getitem__(self, item):
        return self.session.get(item)

    def __setitem__(self, key, value):
        self.session[key] = value
        self.save_session()

    def save_session(self):
        RedisSession.server.set(self.session_id, json.dumps(self.session), ex=config.redis_session_parameter['ex'])

    @staticmethod
    def has_session(session_id):
        return RedisSession.server.exists(session_id)

    @staticmethod
    def get_session(session_id):
        session_str = RedisSession.server.get(session_id)
        if session_str:
            ret = json.loads(str(session_str, encoding="utf8"))
        else:
            ret = None
        return ret

    @staticmethod
    def new_session():
        session_id = str(uuid.uuid4())
        RedisSession.server.set(session_id, json.dumps({}), ex=config.redis_session_parameter['ex'])
        return session_id

    @staticmethod
    def destroy_session(session_id):
        RedisSession.server.delete(session_id)


SESSION_TYPE = dict(
    memory=MemorySession,
    redis=RedisSession,
)


def session_factory():   # 默认内存类型
    st = config.session_type
    if st and st in SESSION_TYPE:
        return SESSION_TYPE[st]
    else:
        raise TypeError("指定的Session类型不存在")

# if __name__ == '__main__':
#     s = SessionMixin()
#     s.session['is_login']=True
#     print(type(s.session['is_login']))
#     del s.session['is_login']
