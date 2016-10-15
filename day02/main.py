#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py

import json, sys, os, datetime
APP_ABS_PATH = os.path.dirname(os.path.abspath(__file__))
CURRENT_USER = ''


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


def save_user_info(user: dict):
    fp = os.path.join(APP_ABS_PATH, user['name'] + '.json')
    try:
        with open(fp, 'w') as fh:
            json.dump(user, fh)
        return True
    except:
        return False


if __name__ == '__main__':
    username = input('Who are you?').strip()
    CURRENT_USER = load_user_info(username)
    if CURRENT_USER:
        print(r'Welcome back %s, you have $%d' % (CURRENT_USER['name'], CURRENT_USER['wallet']))
    else:
        while True:
            wallet = input('You are new, please how much you got? ')
            if wallet.isdigit():
                CURRENT_USER = dict()
                CURRENT_USER['name'] = username
                CURRENT_USER['wallet'] = int(wallet)
                CURRENT_USER['log'] = []
                save_user_info(CURRENT_USER)
                break
            else:
                print('Wrong input format.')
