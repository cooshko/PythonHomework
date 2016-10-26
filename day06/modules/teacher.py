#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
from person import Person
import datetime


class Teacher(Person):
    role = 'teacher'

    def __init__(self, name, gender, age, asset):
        self.name = name
        self.gender = gender
        self.age = age
        self.asset = asset
        self.role = 'teacher'
        self.gain_log = []
        self.lose_log = []
        self.save()

    def gain(self, money, reason):
        """
        上课获得课时费，并记录日志
        :return:
        """
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        money = abs(int(money))
        self.asset += money
        self.gain_log.append([dt, money, reason])
        self.save()

    def lose(self, reason, money=10):
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
        self.save()


if __name__ == '__main__':
    t = Teacher('银角大王', 'male', 29, 15000)
    t = Person.load('teacher', 'alex')
    t.gain(100, "鸡汤课")
    t.lose("差评", money=10)
    print(t.asset)
