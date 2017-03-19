#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import os

BASEDIR = os.path.dirname(os.path.dirname(__file__))

app_settings = {
    'template_path': 'templates',
    'static_path': 'statics',
    'debug': True,
    'autoreload': True,
}

server_port = 8888

db_parameters = {
    'mysql': "mysql+pymysql://root:24559982@192.168.5.138:3306/test",
    'sqlite3': "sqlite+pysqlite:///%s" % os.path.join(BASEDIR, 'db', 'db.sqlite3'),
}

db_type = 'sqlite3'

session_type = 'redis'  # 候选memory、redis
# session_type = 'memory'  # 候选memory、redis

redis_session_parameter = dict(
    host="183.63.156.214",
    # host="119.29.98.82",
    port=16379,
    auth_key="feiliuzhixia3qianchi",
    ex=60*60,  # 过期时间，单位秒
)

redis_chatroom_prefix = '_chatroom'

password_salt = 'SALT'

# 来自客户端的异步请求超时时间，单位秒
future_timeout = 10

# 上传文件的绝对路径
upload_dir = os.path.join(BASEDIR, 'statics', 'upload')

# 上传的URL
upload_url = '/static/upload/'

# 每个上传的文件的体积限制
upload_file_size_limit = 1024 * 1024