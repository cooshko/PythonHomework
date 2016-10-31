#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import socket
import os, sys, datetime
APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(APP_DIR)
from day08.commons.ftp import Ftp
from day08.commons.mymd5 import MyMD5


class FtpClient(Ftp):
    def __init__(self):
        super(FtpClient, self).__init__()

    def connect(self, server_ip, server_port):
        try:
            self.sock.connect((server_ip, server_port))
            print("已连接到服务器...")
            welcome_msg = str(self.sock.recv(1024), encoding='utf8')
            print(welcome_msg)
            return True
        except Exception as e:
            print(e)
            return False

    def auth(self):
        while True:
            username = input("请输入用户名：").strip()
            password = input("请输入密码：").strip()
            password_md5 = MyMD5.encrypt(bytes(password, encoding='utf8'))
            self.sock.send(bytes(username + ':' + password_md5, encoding='utf8'))
            feed_back = self.sock.recv(1024)
            if feed_back == b'OKAY':
                print("验证通过...")
                return True
            elif feed_back == b'AUTH FAILED':
                print("验证失败...")

    def ui(self):
        while True:
            cmd = input(">> ").strip()
            self.sock.send(cmd.encode('utf8'))
            res = self.sock.recv(1024).decode('utf8')
            print(res)



if __name__ == '__main__':
    f = FtpClient()
    f.connect('127.0.0.1', 6969)
    if f.auth():
        f.ui()
    f.sock.close()
