#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import socket
import time
import datetime


class FtpServer(object):
    def __init__(self):
        self.sock = socket.socket()
        self.conn = None
        self.fromip = None

    def start(self, ip, port):
        # 监听端口
        self.sock.bind((ip, port))
        self.sock.listen(5)
        while True:
            # 保持服务器活动
            self.conn, self.fromip = self.sock.accept()
            while True:
                # 获得原始数据
                raw_data = self.conn.recv(1024)
                # 判断接收到的原始数据
                if not raw_data:
                    print(self.fromip, "已经断开连接")
                    break
                # 检查命令


    def ls(self):
        pass

    def cd(self, relate_path):
        pass

    def get(self, fpath):
        pass

    def put(self, fname, fsize):
        pass