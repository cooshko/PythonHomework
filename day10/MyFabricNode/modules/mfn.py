#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : mfn.py

import socket,logging,os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from day10.libs.mylog import MyLog


class Mfn(object):
    def __init__(self, debug=False):
        """

        :param debug:是否调试模式
        """
        self.conn = None
        self.setting = None
        self.debug = debug
        logfile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'log','access.log')
        self.logger = MyLog(logfile=logfile, logconsole=debug)

    def run(self):
        pass




if __name__ == '__main__':
    mfn = Mfn(True)