#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : FtpClient.py

import socket, hashlib, os, sys


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
            self.ui()

    def ui(self):
        while True:
            cmd_str = input(">> ").strip()
            if not cmd_str:
                continue
            cmd = cmd_str.split(maxsplit=1)[0]
            args = cmd_str.replace(cmd, "").lstrip()
            if cmd == 'get':
                self.client_get(args)
            elif cmd == 'put':
                self.client_put(args)
            elif cmd == 'quit':
                self.sock.close()
                break
            else:
                self.sock.send(cmd_str.encode())
                feedback = self.recv_once()
                status, msg = feedback.decode().split("|", maxsplit=1)
                print(msg)

    def client_get(self, args):
        filename = args
        tmp_file = args + '.tmp'
        from_position = 0
        if os.path.isfile(tmp_file):
            # 断点续传
            from_position = os.path.getsize(tmp_file)
            print("正在为你断点续传")
        cmd_str = r'get "{filename:s}" from {position:d}'.format(filename=filename, position=from_position)
        self.sock.send(cmd_str.encode())    # 真正发送命令
        feedback = self.sock.recv(1024).decode()
        status, arg = feedback.split("|")
        # 接收服务器的确认消息，里面包括确认和大小或者拒绝和原因。如果OK则通知服务器开始发送数据，如果拒绝则打印原因
        if status == 'OKAY':
            total_size = int(arg)   # 本次传输总共多少个字节
            received_size = 0       # 已经收到的总字节数
            end_flag = False        # 停止接收标记
            count = 0           # 调试用，统计数据包数量
            m = hashlib.md5()
            self.sock.send(b"START")    # 通知服务器开始传送数据
            with open(tmp_file, 'ab') as fh:
                while not end_flag:
                    count += 1
                    # 设置缓冲大小，最后一个包按照实际字节数读取
                    if total_size - received_size > 1024:
                        buff_size = 1024
                    else:
                        buff_size = total_size - received_size
                        end_flag = True
                    data = self.sock.recv(buff_size)
                    received_size += len(data)  # 统计已接收的字节数
                    fh.write(data)
                    m.update(data)
                    # print(count, len(data))
                    self.process_bar(received_size, total_size)     # 进度条
            d = self.sock.recv(32)  # 接收MD5值，共32个字节
            md5_value = d.decode()
            print()     # 由于进度条功能的缺陷，需要打印一个空行
            # print("total package: ", count)
            print("md5 from server: ", md5_value)
            print("md5 from local : ", m.hexdigest())
            if os.path.isfile(filename):
                # 如果目标文件存在，就先删除
                os.remove(filename)
            os.rename(tmp_file, filename)
        elif status == 'NO':
            # 如果服务器拒绝传送数据，则打印拒绝理由
            print(arg)

    def process_bar(self, m, n):
        """
        进度条
        :param m:
        :param n:
        :return:
        """
        percent = int(m / n * 100)
        arrow = "=" * int(percent/10) + ">"
        msg = "\r" + arrow + " %d%%" % percent
        sys.stdout.write(msg)
        sys.stdout.flush()

    def client_put(self, args):
        filename = args
        if not os.path.isfile(filename):
            print("该本地文件不存在")
            return False
        filesize = os.path.getsize(filename)
        cmd_str = r'put "{filename:s}" {size:d}'.format(filename=filename, size=filesize)
        self.sock.send(cmd_str.encode())    # 发送命令给服务器，put "filename" size
        respond = self.sock.recv(1024).decode()
        status, arg = respond.split("|", maxsplit=1)
        sent_size = 0
        m = hashlib.md5()
        if status == 'OKAY':    # 服务器确认发送，并返回文件起始位置
            start_position = int(arg)
            total_size = filesize - start_position
            with open(filename, 'rb') as fh:
                fh.seek(start_position)
                while sent_size < total_size:
                    data = fh.read(1024)
                    self.sock.send(data)
                    sent_size += len(data)
                    self.process_bar(sent_size, total_size)
                    m.update(data)
            print()
            print("md5 local: ", m.hexdigest())
            result = self.sock.recv(32)     # 服务器返回md5值
            print("md5 server:", result.decode())
            print("DONE")
        else:
            print(arg)

    def send_once(self, bytes_data):
        if not isinstance(bytes_data, bytes):
            raise Exception("发送的数据必须为bytes类型")
        data_size = len(bytes_data)
        if data_size > 0:
            m = hashlib.md5()
            m.update(bytes_data)
            md5_value = m.hexdigest()
            msg = md5_value + "|" + str(data_size)
            self.sock.send(msg.encode())
            self.sock.recv(1024)    # 接收开始信号
            self.sock.send(bytes_data)

    def recv_once(self):
        msg = self.sock.recv(1024)
        md5_value, size_str = msg.decode().split("|", maxsplit=1)
        msg_size = int(size_str)
        recv_data = b''
        self.sock.send(b'START')    # 发送开始信号
        while msg_size - len(recv_data) > 1024:
            recv_data += self.sock.recv(1024)
        else:
            recv_data += self.sock.recv(msg_size - len(recv_data))
        return recv_data


if __name__ == '__main__':
    myclient = FtpClient()
    myclient.start()