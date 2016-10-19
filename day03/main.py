#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py
import json, os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONF_DIR = os.path.join(APP_DIR, 'conf')
CONF_FILE = os.path.join(CONF_DIR, 'haproxy.cfg')
TMP_CONF_FILE = os.path.join(CONF_DIR, 'haproxy.cfg.tmp')


def display_backend_info():
    """
    用户输入backend名称，展示里面的信息
    如找不到backend，则显示提示信息
    """
    global CONF_FILE
    backend_name = input('请输入backend：')
    kw = "backend " + backend_name
    interest_flag = False
    found = False
    print(CONF_FILE)
    with open(CONF_FILE) as conf_f:
        for line in conf_f:
            line = line.rstrip()
            if not interest_flag and line != kw:
                # 如果既不感兴趣，也是不keyword行，将跳过
                continue
            elif interest_flag and not line:
                # 如果是感兴趣的行，且为空行，那么就是感兴趣区域的结束行，关闭感兴趣标记，并跳过
                interest_flag = False
                continue
            else:
                # 其他感兴趣且非空行，或者kw行均打印，并且标记已找到结果
                interest_flag = True
                found = True
            print(line)
    if not found:
        print('没有您要的backend信息。')


def add_record():
    """
    用户输入一个json格式的字符串，往haproxy.cfg里相应的backend添加record
    如果backend不存在，则创建并添加
    如果record不存在，则添加
    如果record已存在，则修改
    :return:
    """
    pass


def remove_record():
    """
    用户输入一个json格式的字符串，往haproxy.cfg里相应的backend删除record
    如果record不存在，则不做任何事情，并返回false
    如果record存在且仅有一条，则删除整个backend信息，返回True
    如果record存在但仍有其他record，则只删除用户指定的record，其他不管，返回True
    :return:
    """
    pass


def switch_file():
    """
    用于切换新旧haproxy.cfg，原有的haproxy.cfg改名类似为haproxy.cfg.v1（版本号结尾）
    新文件（haproxy.cfg.tmp）更名为haproxy.cfg
    :return: 切换成功后返回True
    """

if __name__ == '__main__':
    while True:
        print("""
============================
    1、获取ha记录
    2、增加ha记录
    3、删除ha记录

    (q)退出""")
        user_choice = input('请选择：')
        if user_choice == '1':
            display_backend_info()
        elif user_choice == '2':
            if add_record():
                print("增加成功！")
            else:
                print("增加失败...")
        elif user_choice == '3':
            if remove_record():
                print("删除成功!")
            else:
                print("删除失败...")
        elif user_choice == 'q':
            exit()
        else:
            print("您的输入有误，请重新输入")
