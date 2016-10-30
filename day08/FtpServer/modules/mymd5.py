#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import hashlib


class MyMD5(object):
    @staticmethod
    def encrypt(string: str):
        m = hashlib.md5()
        m.update(string.encode('utf-8'))
        return m.hexdigest()

if __name__ == '__main__':
    print(MyMD5.encrypt('123'))
