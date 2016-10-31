#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
# print(ROOT_DIR)
# print(APP_DIR)
from day08.FtpServer.ftpserver import FtpServer
if __name__ == '__main__':
    f = FtpServer()
    f.start('0.0.0.0', 6969)

