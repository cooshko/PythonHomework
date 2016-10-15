#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : login-emu.py

import getpass, json, sys, os

# data_file是用户信息文件
file_abs_path = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(file_abs_path, 'person_info.json')
# 最大尝试次数
max_fail_times = 3


def write_to_file(person_info):
    with open(data_file, 'w') as df:
        json.dump(person_info, df)


def read_from_file():
    # 尝试读取用户信息文件，如果文件不能读取，或者读取的内容不能被转为dict
    # 则设置一个预设用户
    person_info = dict()
    try:
        with open(data_file) as df:
            person_info = dict(json.load(df))
    except:
        person_info['name'] = 'coosh'
        person_info['password'] = '123456'
        person_info['locked'] = False
        person_info['fail_time'] = 0
        write_to_file(person_info)
    return person_info

# 打印提示input
print(r'Please input username and password')

# 循环开始
while True:
    # 用户输入，由于pycharm下的getpass不正常，所以用input代替
    username_input = input('Username: ')
    # passwd_input = getpass.getpass(prompt='Password: ')
    passwd_input = input('Password: ')

    # 从文件读取用户信息
    person_info = read_from_file()
    # 失败次数记录
    fail_time = person_info['fail_time'] if person_info['fail_time'] else 0

    # 检查用户是否被锁定
    if username_input == person_info['name'] and person_info['locked']:
        # 如果被锁定，打印提示并退出程序
        print('%s is locked, please try again later.' % person_info['name'])

    # 未被锁定时候
    else:
        # 检查用户输入的信息是否匹配
        if username_input == person_info['name'] and passwd_input == person_info['password']:
            # 匹配则打印欢迎信息
            print('Welcome back', username_input)
            # 失败次数清零并写入用户信息文件
            if person_info['fail_time'] > 0:
                person_info['fail_time'] = 0
                write_to_file(person_info)
            break

        # 用户匹配但密码不匹配时
        elif username_input == person_info['name'] and passwd_input != person_info['password']:
            # 失败+1
            fail_time += 1
            person_info['fail_time'] = fail_time
            # 检查是否已到达最大次数
            if fail_time >= max_fail_times:
                # 是，则锁定帐号，并写入到用户信息文件，并打印提示，退出程序
                person_info['locked'] = True
                print('Too many try, %s is locked.' % person_info['name'])
            else:
                # 打印验证失败和剩余次数，并继续循环用户输入
                print('Authentication fail, you have %d chances left.' %
                      (max_fail_times - fail_time))
        else:
            print('No such user.')

        # 回写用户文件
        write_to_file(person_info)
