#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, datetime, json, glob, getpass

SEP_ROW = '=' * 60
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(APP_DIR, 'db')
CURRENT_USER = dict()
LOGINED = False


def auth_deco(func):
    """
    装饰器
    :param func:
    :return:
    """
    while True:
        if LOGINED or auth():
            def wrapper(*args, **kwargs):
                ret = func(*args, **kwargs)
                return ret
            return wrapper


def auth():
    """
    用于认证的函数
    :return:
    """
    global CURRENT_USER, LOGINED
    while True:
        print(SEP_ROW)
        user_input = input('请输入账户名称：').strip()
        pass_input = input('密码：').strip()
        user_json_file = os.path.join(DB_DIR, user_input + '.json')
        if os.path.isfile(user_json_file):
            # 如果用户信息文件存在则尝试读取
            try:
                with open(user_json_file) as f:
                    CURRENT_USER = json.load(f)
                if not CURRENT_USER.get('locked', True):
                    # 如果用户未被锁定
                    if pass_input == CURRENT_USER.get('password'):
                        # 密码匹配
                        LOGINED = True
                        return True
                    else:
                        print("用户名密码不正确")
                        return False
                else:
                    print("该用户已被锁定")
                    return False
            except:
                print("该用户存在异常情况")
                return False
        else:
            # 用户信息文件不存在
            print("该用户不存在。")
            return False


def admin_entry():
    """
    管理员入口
    :return:
    """
    print('i am admin')
    print(CURRENT_USER)


def guest_entry():
    print('i am guest')
    print(CURRENT_USER)


@auth_deco
def select_entry():
    """
    根据用户类型展示不同的入口
    :return:
    """
    global CURRENT_USER
    user_type = CURRENT_USER.get('type')
    if user_type == 'admin':
        admin_entry()
    elif user_type == 'guest':
        guest_entry()





if __name__ == '__main__':
    select_entry()
