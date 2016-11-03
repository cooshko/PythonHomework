#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : ftpserver.py

import os, sys, re, socketserver, logging, hashlib


class FtpServer(socketserver.BaseRequestHandler):
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self, request, client_address, server):
        self.current_user = None
        self.user_quota = 0
        self.pwd = "."
        self.home = "."
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
        self.logger = logging.getLogger('FTP-LOG')
        # 设定全局的日志级别
        self.logger.setLevel(logging.INFO)
        # 将handlers注册到logger去
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        super().__init__(request, client_address, server)

    def handle(self):
        """
        处理请求的方法
        :return:
        """
        conn = self.request
        while True:
            try:
                if not self.__login():
                    # 检查是否通过验证，否的话直接进入下一轮
                    continue
                bdata = conn.recv(1024)     # 接收客户端的指令消息
                if len(bdata) == 0:
                    self.__log("{username:s}已经断开".format(username=self.current_user))
                    break
                cmd_str = bdata.decode().strip()
                cmd = cmd_str.split(maxsplit=1)[0]
                args = cmd_str.replace(cmd, "").lstrip()
                if hasattr(self, "cmd_" + cmd):
                    func = getattr(self, "cmd_" + cmd)
                    func(args)
                else:
                    self.send_once("NO|该指令不存在".encode())
            except Exception as e:
                self.__log("{username:s}已经断开".format(username=self.current_user))
                break

    def __log(self, msg, level=logging.INFO):
        """
        记录访问日志
        :param msg:
        :param level:
        :return:
        """
        # 调用
        msg = "{ip:s}:{port:d} ".format(ip=self.client_address[0], port=self.client_address[1]) + msg
        self.logger.info(msg)

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
                    self.__log(username + "登陆成功")
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
        p = os.path.abspath(p)
        return self.home in p

    def __used_quota(self):
        """
        获取当前用户已使用的配额
        :return: int
        """
        used_quota = 0
        for root, dirname, filenames in os.walk(self.home):
            for filename in filenames:
                used_quota += os.path.getsize(os.path.join(root, filename))
        return used_quota

    def __check_quota(self):
        """
        检查配额
        :return: bool
        """
        pass

    def check_access(self, p):
        """

        :param p: 目标路径
        :return:
        """
        full_path = os.path.abspath(os.path.join(self.home, self.pwd, p.strip()))
        if self.__accessable(full_path):
            return full_path
        else:
            self.send_once("NO|只允许访问你拥有目录".encode())
            return False

    def send_once(self, bytes_data):
        if not isinstance(bytes_data, bytes):
            raise Exception("发送的数据必须为bytes类型")
        data_size = len(bytes_data)
        if data_size > 0:
            m = hashlib.md5()
            m.update(bytes_data)
            md5_value = m.hexdigest()
            msg = md5_value + "|" + str(data_size)
            self.request.send(msg.encode())
            self.request.recv(1024)  # 接收开始信号
            self.request.send(bytes_data)

    def recv_once(self):
        msg = self.request.recv(1024)
        md5_value, size_str = msg.decode().split("|", maxsplit=1)
        msg_size = int(size_str)
        recv_data = b''
        self.request.send(b'START')  # 发送开始信号
        while msg_size - len(recv_data) > 1024:
            recv_data += self.request.recv(1024)
        else:
            recv_data += self.request.recv(msg_size - len(recv_data))
        return recv_data

    def cmd_cd(self, args):
        """
        切换目录
        :return:
        """
        full_path = self.check_access(args)
        if not full_path:
            return False
        self.pwd = full_path.replace(self.home, "").lstrip(os.sep)
        if len(self.pwd) == 0:
            msg = "OKAY|你正在访问家目录"
        else:
            msg = "OKAY|你正在访问" + self.pwd
        self.send_once(msg.encode())

    def cmd_ls(self, args):
        """
        浏览目录
        :return:
        """
        full_path = self.check_access(args)
        if not full_path:
            return False
        dir_list = os.listdir(full_path)
        ret = '.\n..\n'
        for item in dir_list:
            if os.path.isdir(os.path.join(full_path, item)):
                ret += item + os.sep + '\n'
            else:
                ret += item + '\n'
        ret = "OKAY|" + ret.strip()
        self.send_once(ret.encode())

    def cmd_mkdir(self, args):
        """
        创建目录
        :return:
        """
        full_path = self.check_access(args)
        if not full_path:
            return False
        if os.path.isdir(full_path):
            ret = "NO|目录已存在，不能重复创建"
        else:
            os.mkdir(full_path)
            ret = "OKAY|创建完成"
        self.send_once(ret.encode())

    def cmd_rm(self, args):
        """
        删除目录或者文件
        :return:
        """
        full_path = self.check_access(args)
        if not full_path:
            return False
        if os.path.isfile(full_path):
            os.remove(full_path)
            msg = "OKAY|DONE"
            self.__log("{username:s}删除了文件{file:s}".format(username=self.current_user, file=full_path))
        elif os.path.isdir(full_path):
            import shutil
            shutil.rmtree(full_path)
            msg = "OKAY|DONE"
        else:
            msg = "NO|路径不存在"
        self.send_once(msg.encode())

    def cmd_du(self, args):
        """
        获取当前用户的配额信息
        :param args:
        :return:
        """
        used_quota = self.__used_quota()
        remain_quota = self.user_quota - used_quota if self.user_quota - used_quota > 0 else 0
        msg = "OKAY|你的配额是%d，已使用%d，剩余%d" % (self.user_quota, used_quota, remain_quota)
        self.send_once(msg.encode())

    def cmd_get(self, args):
        """
        客户端获取文件
        :param args: 类似get "filename" from 0
        :return:
        """
        filename = re.search(r'.*"(.*)".*', args).group(1)  # 要获取的文件名
        start_position = int(re.search(r'.*from (\d+)$', args).group(1))    # 断点续传的起始位
        full_path = self.check_access(filename)     # 检查是否允许访问并返回绝对路径
        if not full_path:
            # 如果不允许访问则返回
            return False
        if not os.path.isfile(full_path):
            self.request.send("NO|文件不存在".encode())
        else:
            total_size = os.path.getsize(full_path) - start_position    # 要发送的总字节数
            sent_size = 0    # 已发送的字节数
            m = hashlib.md5()
            self.request.send(("OKAY|" + str(total_size)).encode())     # 发送确认和即将发送的大小
            signal = self.request.recv(1024)     # 获取客户端的开始信号
            if signal == b'START':
                with open(full_path, 'rb') as fh:
                    fh.seek(start_position)     # 根据断点定位文件
                    end_flag = False
                    count = 0
                    while not end_flag:
                        count += 1
                        if total_size - sent_size > 1024:
                            buff_size = 1024
                        else:
                            buff_size = total_size - sent_size
                            end_flag = True
                        data = fh.read(buff_size)  # 读1024个字节
                        #print(data)
                        self.request.send(data)  # 发送
                        sent_size += len(data)
                        m.update(data)
                        #print(count, len(data))
                self.request.send(m.hexdigest().encode())
                self.__log("{username:s}下载了文件{file:s}".format(username=self.current_user, file=full_path))

    def cmd_put(self, args):
        """
        上传文件
        :param args:
        :return:
        """
        filename = re.search(r'"(.*)".*', args).group(1)
        total_size = int(re.search(r'".*" (\d+)', args).group(1))
        full_path = self.check_access(filename)  # 检查是否允许访问并返回绝对路径
        if not full_path:
            # 如果不允许访问则返回
            return False
        tmp_file = full_path + ".tmp"
        start_position = 0
        if os.path.isfile(tmp_file):
            start_position = os.path.getsize(tmp_file)
            total_size -= start_position
        # 检查配额
        used_quota = self.__used_quota()
        if self.user_quota - used_quota < total_size:
            msg = "NO|你的磁盘配额不足"
            self.request.send(msg.encode())
            return
        # 通过所有检查
        msg = "OKAY|%d" % start_position
        self.request.send(msg.encode())
        end_flag = False
        received_size = 0
        m = hashlib.md5()
        with open(tmp_file, 'ab') as fh:
            while not end_flag:
                if total_size - received_size > 1024:
                    buff_size = 1024
                else:
                    buff_size = total_size - received_size
                    end_flag = True
                data = self.request.recv(buff_size)
                fh.write(data)
                received_size += len(data)
                m.update(data)
        self.request.send(m.hexdigest().encode())
        if os.path.isfile(full_path):
            os.remove(full_path)
        os.rename(tmp_file, full_path)
        self.__log("{username:s}上传了文件{file:s}".format(username=self.current_user, file=full_path))

if __name__ == '__main__':
    myserver = socketserver.ThreadingTCPServer(("0.0.0.0", 9999), FtpServer)
    myserver.serve_forever()