#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py

import sys, os, socketserver
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT_DIR)
from day09.FtpServer.modules.FtpServer import FtpServer

if __name__ == '__main__':
    myserver = socketserver.ThreadingTCPServer(("0.0.0.0", 9999), FtpServer)
    myserver.serve_forever()