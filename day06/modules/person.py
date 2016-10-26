#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import os
import pickle
"""
Person类是admin、student、teacher的基类
"""


class Person:
    APP_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_DIR = os.path.join(APP_DIR, 'db')

    @staticmethod
    def load(role, name):
        full_path = os.path.join(Person.DB_DIR, role, name + '.pickle')
        try:
            with open(full_path, 'rb') as f:
                ret = pickle.load(f)
            return ret
        except:
            return False

    def save(self):
        full_path = os.path.join(Person.DB_DIR, self.role, self.name + '.pickle')
        try:
            with open(full_path, 'wb') as f:
                pickle.dump(self, f)
            return True
        except Exception as e:
            return False

    @staticmethod
    def test():
        print("Person")

    def auth(self, username, password):
        return self.name == username and self.password == password

    def change_password(self, passwd):
        self.password = passwd
        self.save()

if __name__ == '__main__':
    p = Person.load('teacher', 'alex')
