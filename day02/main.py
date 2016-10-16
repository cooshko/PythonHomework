#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py

import json, sys, os, datetime
APP_ABS_PATH = os.path.dirname(os.path.abspath(__file__))
CURRENT_USER = ''


# 根据用户名（字符串），从文件读取用户信息，如果没有文件或者无法转换都会返回False
def load_user_info(user: str):
    try:
        if not user.strip():
            raise Exception
        fp = os.path.join(APP_ABS_PATH, user + '.json')
        with open(fp) as fh:
            ret = json.load(fh)
        return ret
    except Exception as e:
        return False


# 将用户信息（字典），保存到文件中去，以便以后读取
def save_user_info(user: dict):
    if not user:
        return False
    fp = os.path.join(APP_ABS_PATH, user['name'] + '.json')
    try:
        with open(fp, 'w') as fh:
            json.dump(user, fh)
        return True
    except:
        return False


# 充值函数
def user_recharge_money(user: dict):
    if not isinstance(user, dict):
        raise TypeError('user should be dict.')
    if user:
        print('当前余额：%d' % user['wallet'])
    else:
        user['wallet'] = 0
    while True:
        recharge = input('请输入你要充值的金额：').strip()
        if recharge.isdigit():
            user['wallet'] += int(recharge)
            print('充值后余额为：%d' % user['wallet'])
            save_user_info(user)
            return True
        else:
            print('输入格式有误，请重新输入')

if __name__ == '__main__':
    # 用户输入身份信息
    username = input('请问您是? ').strip()

    sep_row = '='*50
    print(sep_row)
    # 从文件读取用户信息，如果没有，则让用户充值
    CURRENT_USER = load_user_info(username)
    if CURRENT_USER:
        print(r'欢迎回来 %s，您的余额是%d' % (CURRENT_USER['name'], CURRENT_USER['wallet']))
    else:
        print('你是新顾客')
        CURRENT_USER = dict()
        user_recharge_money(CURRENT_USER)
        CURRENT_USER['name'] = username
        CURRENT_USER['log'] = []
        save_user_info(CURRENT_USER)

    # 打印入口
    while True:
        print(sep_row)
        entry_choice = input(r'''请选择您要做什么:
1. 购物
2. 充值

(q) 退出
请选择：''')
        if entry_choice == 'q':
            exit()
        elif entry_choice == '1':
            pass
        elif entry_choice == '2':
            user_recharge_money(CURRENT_USER)
        else:
            print('您的输入有误，请重新输入')
