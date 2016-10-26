#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : admin.py

import datetime
from person import Person
from student import Student
from teacher import Teacher
from lesson import Lesson


class Admin(Person):
    def __init__(self):
        """
        管理员初始化
        """
        self.name = 'admin'
        self.password = 'admin'
        self.role = 'admin'
        self.save()

    def create_teacher(self):
        t_name = input("讲师名字：").strip()
        teacher = Teacher.load('teacher', t_name)
        if teacher:
            print("该讲师已存在")
            return False
        t_gender = input("性别：").strip()
        t_age = int(input("年龄：").strip())
        t_asset = int(input("现有资产：").strip())
        t = Teacher(t_name, t_gender, t_age, t_asset)
        if t:
            print("创建老师成功")
            return True

    def create_lesson(self):
        """
        创建课程
        """
        l_name = input("课程名字：").strip()
        lesson = Lesson.load(l_name)
        if lesson:
            print("该课程已存在")
            return False
        teacher = input("负责讲师：").strip()
        l_teacher = Teacher.load('teacher', teacher)
        if not l_teacher:
            print("该讲师不存在，请先创建")
            return False
        l_classtime = input("课堂时间：").strip()
        l_money = int(input("课时费：").strip())
        l_skill = input("课程内容：").strip()
        l = Lesson(l_name, l_money, l_classtime, l_skill, l_teacher)
        if l:
            print("创建课程成功")
            return True

    def create_student(self):
        """
        创建学生
        :return:
        """
        s_name = input("学生名字：").strip()
        stu = Student.load('student', s_name)
        if stu:
            print("该学生已存在")
            return False
        s_gender = input("性别：").strip()
        s_age = int(input("年龄：").strip())
        s_password = input("初始密码（留空则为123）：").strip()
        if not s_password:
            s_password = '123'
        s = Student(s_name, s_gender, s_age, s_password)
        if s:
            print("创建学生成功")
            return True

    def display_teacher_log(self):
        while True:
            t_name = input("输入要查看的讲师名字（留空返回）：").strip()
            if t_name:
                t = Teacher.load('teacher', t_name)
                if t:
                    print("该老师的资产目前是（明细如下）：", t.asset)
                    print("收入明细")
                    for record in t.gain_log:
                        print(record[0], record[1], record[2])
                    print("扣钱明细")
                    for record in t.lose_log:
                        print(record[0], record[1], record[2])
                else:
                    print("你输入的讲师不存在")
            else:
                return


    def todo(self):
        while True:
            print('=' * 40)
            command_list = ['创建课程', '创建讲师信息', '创建学生信息', '修改密码', '查看讲师资产', '退出']
            for item in enumerate(command_list):
                print(item[0], item[1])
            choice = input("请选择：").strip()
            if choice == '0':
                self.create_lesson()
            elif choice == '1':
                self.create_teacher()
            elif choice == '2':
                self.create_student()
            elif choice == '3':
                self.change_password()
            elif choice == '4':
                self.display_teacher_log()
            elif choice == '5':
                return True
