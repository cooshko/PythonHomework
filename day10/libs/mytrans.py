#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import hashlib, os


class MyTransMixIn(object):
    @staticmethod
    def send_once(conn, bytes_data):
        if not isinstance(bytes_data, bytes):
            raise Exception("发送的数据必须为bytes类型")
        data_size = len(bytes_data)
        if data_size > 0:
            m = hashlib.md5()
            m.update(bytes_data)
            md5_value = m.hexdigest()
            msg = md5_value + "|" + str(data_size)
            conn.sendall(msg.encode())
            conn.recv(1024)  # 接收开始信号
            conn.sendall(bytes_data)
            conn.recv(32)

    @staticmethod
    def recv_once(conn):
        msg = conn.recv(1024)
        m = hashlib.md5()
        if not msg:
            raise ValueError("连接中断")
        md5_value, size_str = msg.decode().split("|", maxsplit=1)
        msg_size = int(size_str)
        recv_data = b''
        conn.sendall(b'START')  # 发送开始信号
        while msg_size - len(recv_data) > 1024:
            recv_data += conn.recv(1024)
        else:
            recv_data += conn.recv(msg_size - len(recv_data))
        m.update(recv_data)
        conn.sendall(m.hexdigest().encode())
        return recv_data

    @staticmethod
    def send_file(sock, local_file):
        m = hashlib.md5()
        success = False
        description = ""
        if local_file:
            if os.path.isfile(local_file):
                # 文件存在
                filesize = os.path.getsize(local_file)
                filename = os.path.basename(local_file)
                file_info = ("{filename:s}|{size:d}".format(filename=filename, size=filesize)).encode(encoding='utf8')
                sock.sendall(file_info)  # 先发送命令和文件大小
                signal = sock.recv(1024).decode()  # 接收方发来信号
                if signal.startswith("START"):
                    # 如果接收方发出START信号，开始传送数据
                    with open(local_file, 'rb') as fh:
                        sent_size = 0
                        while sent_size < filesize:
                            data = fh.read(1024)
                            sent_size += len(data)
                            m.update(data)
                            sock.sendall(data)  # 发送1024字节数据
                    # 最后交换md5
                    sock.sendall(m.hexdigest().encode())
                    md5_from_node = sock.recv(32).decode()
                    if md5_from_node == m.hexdigest():
                        success = True
                        description = "完成传送文件"
                    else:
                        description = "传送文件出错"
                else:
                    # 如果接收方不同意，则输出拒绝理由
                    reason = signal.split("|", maxsplit=1)[1]
                    description = reason
            else:
                description = "该本地文件不存在"
        else:
            description = "请提供本地文件"
        return success, description

    @staticmethod
    def recv_file(sock, tmp_dir="."):
        m = hashlib.md5()
        file_info = sock.recv(1024).decode()
        # 对应cmd_msg = ("{filename:s}|{size:d}".format(filename=filename, size=filesize)).encode()
        filename = file_info.split("|")[0]
        filesize = int(file_info.split("|")[1])
        tmp_dir = os.path.abspath(tmp_dir)

        # 检查是否存在临时目录，如果不存在，则创建
        if not os.path.isdir(tmp_dir):
            os.mkdir(tmp_dir)
        file_abs_path = os.path.join(tmp_dir, filename)
        tmp_file_abs_path = file_abs_path + ".tmp"
        # 发出信号让发送方开始传输数据
        sock.sendall(b"START")
        recv_size = 0   # 已接收到的字节数
        with open(tmp_file_abs_path, 'ab') as fh:
            while recv_size < filesize:
                if filesize - recv_size > 1024:
                    data = sock.recv(1024)
                else:
                    data = sock.recv(filesize - recv_size)
                fh.write(data)
                m.update(data)
                recv_size += len(data)
        # 接收完文件数据后，双方交换md5
        md5_from_sender = sock.recv(32).decode()
        sock.sendall(m.hexdigest().encode())
        if md5_from_sender == m.hexdigest():
            if os.path.isfile(file_abs_path):
                os.remove(file_abs_path)
            os.rename(tmp_file_abs_path, file_abs_path)
        else:
            # 接收出错，则删除临时文件
            os.remove(tmp_file_abs_path)
