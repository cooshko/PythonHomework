#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : lesson.class.py
import glob
import os
import pickle
from teacher import Teacher


class Lesson:
    APP_DIR = os.path.dirname(os.path.dirname(__file__))
    LESSON_DB_DIR = os.path.join(APP_DIR, 'db', 'lesson')

    def __init__(self, name, money, classtime, teacher: Teacher):
        self.name = name
        self.teacher = Teacher.load('teacher', teacher)
        self.teacher = teacher
        self.money = money
        self.classtime = classtime

    def lesson_on(self):
        print('上%s' % self.name)
        self.teacher.gain(self.money, self.name)

    def rated(self, score):
        if score == 0:
            self.teacher.lose(reason="差评", money=10)

    def save(self):
        full_path = os.path.join(Lesson.LESSON_DB_DIR, self.name + '.pickle')
        try:
            with open(full_path, 'wb') as f:
                pickle.dump(self, f)
            return True
        except Exception as e:
            return False

    @staticmethod
    def load(name):
        full_path = os.path.join(Lesson.LESSON_DB_DIR, name + '.pickle')
        try:
            with open(full_path, 'rb') as f:
                ret = pickle.load(f)
            return ret
        except Exception as e:
            return False

    @staticmethod
    def load_all_lesson():
        ret = []
        pfiles = glob.glob(os.path.join(Lesson.LESSON_DB_DIR, '*'))
        for pfile in pfiles:
            with open(pfile, 'rb') as f:
                lesson = pickle.load(f)
                ret.append(lesson)
        return ret


if __name__ == '__main__':
    l = Lesson('Python课', 100, '19:00', '银角大王')
    l.save()
    # l = Lesson.load("鸡汤课")
    # print(l.teacher.asset)
    # print(Lesson.load_all_lesson()[0].name)