#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
from person import Person
import datetime


class Teacher(Person):
    def __init__(self, name, gender, age, asset):
        self.name = name
        self.gender = gender
        self.age = age
        self.asset = asset
        self.role = 'teacher'
        self.gain_log = []
        self.lose_log = []

    def gain(self, money, reason):
        """
        上课获得课时费，并记录日志
        :return:
        """
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        money = abs(money)
        self.asset += money
        self.gain_log.append([dt, money, reason])

    def lose(self, money, reason):
        """
        扣钱、理由
        :param money:
        :param reason:
        :return:
        """
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        money = -1 * abs(money)
        self.asset += money
        self.lose_log.append([dt, money, reason])


if __name__ == '__main__':
    # t = Teacher('alex', 'male', 30, 15000)
    # t.save()
    t = Person.load('teacher', 'alex')
    t.gain(100, "鸡汤课")
    t.lose(10, "差评")
    print(t.asset)
