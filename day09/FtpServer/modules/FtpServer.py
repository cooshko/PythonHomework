#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : ftpserver.py

import os, sys, re,socketserver


class FtpServer(socketserver.BaseRequestHandler):
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self, request, client_address, server):
        self.current_user = None
        self.user_quota = 0
        self.pwd = "."
        self.home = "."
        super().__init__(request, client_address, server)

    def handle(self):
        """
        处理请求的方法
        :return:
        """
        conn = self.request
        while True:
            if not self.__login():
                continue
            bdata = conn.recv(1024)
            if len(bdata) == 0:
                break
            cmd_str = bdata.decode().strip()
            cmd = cmd_str.split(maxsplit=1)[0]
            args = cmd_str.replace(cmd, "").lstrip()
            if hasattr(self, cmd):
                func = getattr(self, cmd)
                func(args)

    def __login(self):
        """
        认证函数
        :return:bool
        """
        if self.current_user:
            # 已经登录
            return True
        else:
            # 尝试认证
            bdata = self.request.recv(1024)
            username, passmd5 = bdata.decode().split(":")   # 客户端发过来的格式，应该为“username:password_md5”
            user_info_file = os.path.join(FtpServer.ROOT_DIR,  'conf', username + '.txt')   # 生成用户信息文件路径
            if os.path.isfile(user_info_file):
                # 如果该用户文件存在，读取文件内容
                with open(user_info_file) as f:
                    p, user_quota = f.readline().strip().split(":")
                if p == passmd5:
                    # 如果密码能匹配上，则配置实例中用户信息，并返回通知给客户端，最后返回True
                    self.current_user = username
                    self.user_quota = int(user_quota)
                    self.home = os.path.join(FtpServer.ROOT_DIR, 'home', self.current_user)
                    self.request.send("OKAY|欢迎".encode())
                    return True
                else:
                    # 密码不对
                    self.request.send("FAIL|认证失败".encode())
                    return False
            else:
                # 用户文件不存在
                self.request.send("FAIL|该用户不存在。".encode())
                return False


    def __accessable(self, p):
        """
        检查目标是否在家目录下
        :param p:目标绝对路径
        :return: bool
        """
        pass

    def __check_quota(self):
        """
        检查配额
        :return: bool
        """
        pass

    def ls(self):
        """
        浏览当前目录
        :return:
        """
        pass

    def mkdir(self, args):
        """
        创建目录
        :return:
        """
        pass

    def rm(self, args):
        """
        删除目录或者文件
        :return:
        """
        pass

    def get(self, args):
        """
        获取文件
        :return:
        """
        pass

    def put(self, args):
        """
        上传文件
        :param args:
        :return:
        """

if __name__ == '__main__':
    myserver = socketserver.ThreadingTCPServer(("0.0.0.0", 9999), FtpServer)
    myserver.serve_forever()