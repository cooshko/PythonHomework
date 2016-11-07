#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import hashlib


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
            conn.send(msg.encode())
            conn.recv(1024)  # 接收开始信号
            conn.send(bytes_data)

    @staticmethod
    def recv_once(conn):
        msg = conn.recv(1024)
        md5_value, size_str = msg.decode().split("|", maxsplit=1)
        msg_size = int(size_str)
        recv_data = b''
        conn.send(b'START')  # 发送开始信号
        while msg_size - len(recv_data) > 1024:
            recv_data += conn.recv(1024)
        else:
            recv_data += conn.recv(msg_size - len(recv_data))
        return recv_data

