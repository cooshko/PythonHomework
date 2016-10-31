#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
# print(ROOT_DIR)
# print(APP_DIR)
from day08.FtpClient.ftpclient import FtpClient
if __name__ == '__main__':
    f = FtpClient()
    f.connect('127.0.0.1', 6969)
    f.conn.send(b'ls')

