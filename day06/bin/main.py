#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py
import os, sys
APP_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(APP_DIR, 'modules'))
from admin import Admin
from student import Student
from lesson import Lesson

while True:
    username = input("请输入用户名：").strip()
    password = input("密码：").strip()
    if username == 'admin':
        admin = Admin.load('admin', username)
        if admin:
            # 存在admin
            if not admin.auth(username, password):
                print("你输入的密码不正确")
                continue
        else:
            # admin不存在，创建一个默认的，并执行admin任务
            admin = Admin()
        admin.todo()
    else:
        stu = Student.load('student', username)
        if stu:
            # 存在该学生
            if stu.auth(username, password):
                # 认证通过，则执行student的任务
                stu.todo()
            else:
                print("你输入的密码不正确")
                continue
        else:
            # 学生信息不存在
            print("该用户不存在")
            continue
