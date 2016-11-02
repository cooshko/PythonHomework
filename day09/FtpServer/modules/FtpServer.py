#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : ftpserver.py

import os, sys, re, socketserver, logging


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
                # 检查是否通过验证，否的话直接进入下一轮
                continue
            bdata = conn.recv(1024)     # 接收客户端的指令消息
            if len(bdata) == 0:
                self.__log("{client_ip:s}已经断开".format(client_ip=self.client_address[0]))
                break
            cmd_str = bdata.decode().strip()
            cmd = cmd_str.split(maxsplit=1)[0]
            args = cmd_str.replace(cmd, "").lstrip()
            if hasattr(self, cmd):
                func = getattr(self, cmd)
                func(args)

    def setup(self):
        connect_msg = "{client_ip:s}已连接".format(client_ip=self.client_address[0])
        self.__log(connect_msg)

    def __log(self, msg, level=logging.INFO):
        """
        记录访问日志
        :param msg:
        :param level:
        :return:
        """
        log_path = os.path.join(FtpServer.ROOT_DIR, 'log', 'access.log')
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%F %H:%M:%S")
        # 设定handler，fh是文件，ch是console；其中文件记录全部的日志，console只输出Warning级别以上的日志
        fh = logging.FileHandler(filename=log_path, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        # 设定logger，FTP-LOG是这个logger的name
        logger = logging.getLogger('FTP-LOG')
        # 设定全局的日志级别
        logger.setLevel(level)
        # 将handlers注册到logger去
        logger.addHandler(fh)
        logger.addHandler(ch)
        # 调用
        logger.info(msg)

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