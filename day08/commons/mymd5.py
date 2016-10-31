#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import hashlib


class MyMD5(object):
    @staticmethod
    def encrypt(bstring: bytes):
        m = hashlib.md5()
        m.update(bstring)
        return m.hexdigest()

if __name__ == '__main__':
    print(MyMD5.encrypt(b'123'))
    print(MyMD5.encrypt(b'123'))
