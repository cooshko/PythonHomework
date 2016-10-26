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
        teacher = Teacher.load(t_name)
        if teacher:
            print("该讲师已存在")
            return False
        t_gender = input("性别：").strip()
        t_age = int(input("年龄：").strip())
        t_asset = input("现有资产：").strip()
        Teacher(t_name, t_gender, t_age, t_asset)
        return True

    def create_lesson(self):
        """
        创建课程
        """
        l_name = input("课程名字：").strip()
        lesson = Lesson.load(l_name)
        if not lesson:
            print("该课程已存在")
            return False
        teacher = input("负责讲师：").strip()
        l_teacher = Teacher.load(teacher)
        if not l_teacher:
            print("该讲师不存在，请先创建")
            return False
        l_classtime = input("课堂时间：").strip()
        l_money = int(input("课时费：").strip())
        l_skill = input("课程内容：").strip()
        Lesson(l_name, l_money, l_classtime, l_skill, l_teacher)
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
        Student(s_name, s_gender, s_age, s_password)
        return True