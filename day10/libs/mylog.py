#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : mylog.py

import logging,os


class MyLog(logging.Logger):
    def __init__(self, logfile=None, logconsole=False):
        super(MyLog, self).__init__("MyLog")
        fmt = "%(asctime)s - %(levelname)s - %(message)s"
        date_fmt = "%F %H:%M:%S"
        self.setLevel(logging.DEBUG)
        if logfile and os.path.isfile(logfile):
            fh = logging.FileHandler(filename=logfile, encoding='utf-8')
            ff = logging.Formatter(fmt=fmt, datefmt=date_fmt)
            fh.setFormatter(ff)
            fh.setLevel(logging.DEBUG)
            self.addHandler(fh)
        if logconsole:
            ch = logging.StreamHandler()
            cf = logging.Formatter(fmt=fmt, datefmt=date_fmt)
            ch.setFormatter(cf)
            ch.setLevel(logging.DEBUG)
            self.addHandler(ch)


