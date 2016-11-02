#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : FtpClient.py

import socket, hashlib


class FtpClient(object):
    def __init__(self):
        self.sock = socket.socket()
        self.server = ("localhost", 9999)

    def connect(self):
        self.sock.connect(self.server)
        while True:
            username = input("用户名：").strip()
            password = input("密码：").strip()
            m = hashlib.md5()
            m.update(password.encode())
            passmd5 = m.hexdigest()
            send_data = username + ":" + passmd5
            self.sock.send(send_data.encode())
            recv_data = self.sock.recv(1024)
            status, msg = recv_data.decode().split("|")
            print("服务器：", msg)
            if status == "OKAY":
                return True

    def start(self):
        if self.connect():
            pass

if __name__ == '__main__':
    myclient = FtpClient()
    myclient.start()