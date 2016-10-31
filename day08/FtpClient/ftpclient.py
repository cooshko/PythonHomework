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
        # try:
            self.sock.connect((server_ip, server_port))
            print("已连接到服务器...")
            self.conn = self.sock
            welcome_msg = str(self.recv(), encoding='utf8')
            print(welcome_msg)
            return True
        # except Exception as e:
        #     print(e)
        #     return False

    def auth(self):
        while True:
            username = input("请输入用户名：").strip()
            password = input("请输入密码：").strip()
            password_md5 = MyMD5.encrypt(bytes(password, encoding='utf8'))
            self.send(bytes(username + ':' + password_md5, encoding='utf8'))
            feed_back = self.recv()
            if feed_back == b'OKAY':
                print("验证通过...")
                return True
            elif feed_back == b'AUTH FAILED':
                print("验证失败...")

    def ui(self):
        while True:
            cmd = input(">> ").strip()
            if cmd:
                if str(cmd).lower().startswith('get '):
                    self.get(cmd)
                elif str(cmd).lower().startswith('put '):
                    self.put(cmd)
                elif str(cmd).lower() == 'exit':
                    self.conn.close()
                    return True
                else:
                    self.send(cmd.encode('utf8'))
                    res = self.recv().decode('utf8')
                    print(res)

    def get(self, cmd):
        """
        客户端获取文件
        :return:
        """
        if not self.conn:
            raise Exception("当前没有连接")
        self.send(cmd.encode('utf8'))
        feedback = self.recv().decode('utf8')   # OK|FILENAME|SIZE or NO|MSG
        status = feedback.split("|")[0]
        filedata = b''
        if status == 'OK':
            filename = feedback.split("|")[1]
            filesize = int(feedback.split("|")[2])
            self.send(b'START')
            while len(filedata) < filesize:
                filedata += self.recv()
            with open(filename, 'wb') as fh:
                fh.write(filedata)
            print("接收完毕")
        else:
            msg = feedback.split("|")[1]
            print(msg)

    def put(self, cmd):
        if not self.conn:
            raise Exception("当前没有连接")
        filename = cmd.replace('put ', '').strip()
        if filename:
            if os.path.isfile(filename):
                filesize = os.path.getsize(filename)
                self.send(bytes(cmd.rstrip() + ' ' + str(filesize), encoding='utf8'))
                msg = self.recv().decode('utf8')
                if msg == "START":
                    with open(filename, 'rb') as fh:
                        filedata = fh.read()
                    self.send(filedata)
                    feedback = self.recv().decode(encoding='utf8')
                    print(feedback)
                else:
                    print(msg)

            else:
                print("该本地文件不存在")
        else:
            print("请提供文件")




if __name__ == '__main__':
    while True:
        f = FtpClient()
        f.connect('127.0.0.1', 6969)
        if f.auth():
            f.ui()
