#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import socket
import time
import datetime
import os, sys, shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
from day08.commons.ftp import Ftp


class FtpServer(Ftp):
    HOME_DIR = os.path.join(APP_DIR, 'home')
    DB_FILE = os.path.join(APP_DIR, 'db', 'user.db')

    def __init__(self):
        super(FtpServer, self).__init__()
        self.fromip = None
        self.current_user = None
        self.pwd = '.'

    def start(self, ip, port):
        # 监听端口
        self.sock.bind((ip, port))
        self.sock.listen(5)
        while True:
            print("等待新的会话...")
            # 保持服务器活动
            self.conn, self.fromip = self.sock.accept()
            print("%s:%s 已连接..." % (self.fromip[0], self.fromip[1]))
            self.send(b'NEED AUTH')
            while True:
                try:
                    if not self.current_user:
                        # 如果用户未登录
                        self.current_user = self.auth()
                        if self.current_user:
                            print("%s 登录成功..." % self.current_user)
                    else:
                        # 用户已经登录，侦听用户指令
                        cmd_str = self.recv().decode('utf8')
                        cmd = cmd_str.split(maxsplit=1)[0].lower()
                        args = cmd_str.replace(cmd, '').lstrip()
                        # 使用反射调用方法
                        if hasattr(self, cmd):
                            func = getattr(self, cmd)
                            res = func(args)
                        else:
                            res = b'unknown command'
                        self.send(res)
                except Exception as e:
                    print('%s 已经断开' % self.current_user)
                    self.current_user = None
                    self.conn.close()
                    break

    def auth(self):
        raw_data = self.recv()
        auth_msg = str(raw_data, encoding='utf8')
        username = auth_msg.split(':')[0]
        with open(FtpServer.DB_FILE) as fh:
            res = auth_msg in fh.read()
        if res:
            self.pwd = '.'
            self.send(b'OKAY')
        else:
            self.send(b'AUTH FAILED')
        return username if res else False

    def ls(self, relate_path):
        full_path = os.path.abspath(os.path.join(FtpServer.HOME_DIR, self.current_user, self.pwd, relate_path))
        # print(full_path)
        if not os.path.join(FtpServer.HOME_DIR, self.current_user) in full_path:
            ret = "你只能访问自己的目录".encode('utf8')
            return ret
        if not os.path.isdir(full_path):
            ret = "你要访问的目录不存在".encode('utf8')
            return ret
        dir_list = os.listdir(full_path)
        ret = '.\n..\n'
        for item in dir_list:
            if os.path.isdir(os.path.join(full_path, item)):
                ret += item + os.sep + '\n'
            else:
                ret += item + '\n'
        return ret.strip().encode(encoding='utf8')

    def cd(self, relate_path):
        user_home = os.path.join(FtpServer.HOME_DIR, self.current_user)
        # 检查切换的目录是否属于用户自己的
        full_path = os.path.abspath(os.path.join(user_home, self.pwd, relate_path))
        # print(full_path)
        if not os.path.join(FtpServer.HOME_DIR, self.current_user) in full_path:
            ret = "你只能访问自己的目录".encode('utf8')
            return ret
        if not os.path.isdir(full_path):
            ret = "你要访问的目录不存在".encode('utf8')
            return ret
        # 切换目录
        self.pwd = full_path.replace(user_home + os.sep, '')
        ret = b"DONE"
        return ret

    def mkdir(self, dirname):
        dirname = dirname.strip()
        if not dirname:
            ret = "目录名称不能为空".encode('utf8')
            return ret
        full_path = os.path.abspath(os.path.join(FtpServer.HOME_DIR, self.current_user, self.pwd, dirname))
        # print(full_path)
        if os.path.isdir(full_path):
            ret = "目录已存在，不能重复创建".encode('utf8')
        else:
            os.mkdir(full_path)
            ret = b"DONE"
        return ret

    def rm(self, fpath):
        """
        删除目录或者路径
        注意该命令是直接递归删除
        :param fpath:
        :return:
        """
        if not self.accessable(fpath):
            ret = "你只能访问自己的目录".encode('utf8')
            return ret
        full_path = os.path.abspath(os.path.join(FtpServer.HOME_DIR, self.current_user, self.pwd, fpath))
        if not os.path.exists(full_path):
            ret = "目标不存在，不能删除".encode('utf8')
        else:
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            ret = b"DONE"
        return ret

    def get(self, filename):
        # print(filename)
        if not self.accessable(filename):
            ret = "NO|你只能访问自己的目录".encode('utf8')
            return ret
        full_path = os.path.abspath(os.path.join(FtpServer.HOME_DIR, self.current_user, self.pwd, filename))
        # 检查文件是否存在
        if os.path.isfile(full_path):
            filesize = os.path.getsize(full_path)
            self.send(bytes("OK|%s|%d" % (filename, filesize), encoding='utf8'))
            if self.recv() == b'START':
                with open(full_path, 'rb') as fh:
                    filedata = fh.read()
                return filedata
        else:
            ret = "NO|文件不存在".encode('utf8')
            return ret

    def put(self, args):    # 收到的格式应该是filename filesize
        filesize = int(args.split()[-1])
        filename = args.replace(str(filesize), '').strip()
        if not self.accessable(filename):
            ret = "NO|你只能访问自己的目录".encode('utf8')
            return ret

        full_path = os.path.abspath(os.path.join(FtpServer.HOME_DIR, self.current_user, self.pwd, filename))
        received_data = b''
        self.send(b'START')
        while len(received_data) < filesize:
            received_data += self.recv()
        with open(full_path, 'wb') as fh:
            fh.write(received_data)
        return b'DONE'

    def accessable(self, rpath):
        full_path = os.path.abspath(os.path.join(FtpServer.HOME_DIR, self.current_user, self.pwd, rpath))
        return os.path.join(FtpServer.HOME_DIR, self.current_user) in full_path


if __name__ == '__main__':
    f = FtpServer()
    f.start('0.0.0.0', 6969)
