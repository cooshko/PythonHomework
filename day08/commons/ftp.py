#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import socket, os, sys
APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(APP_DIR)
from day08.commons.mymd5 import MyMD5


class Ftp(object):
    def __init__(self):
        self.sock = socket.socket()
        self.conn = None
        self.pwd = '.'

    def send(self, bytes_obj):
        """
        发送方封装的方法，为解决粘包，每次先发送md5值以及大小，收到对端确认才发原始数据
        :param bytes_obj:必须为bytes类型，否则发起异常
        :return:
        """
        if not isinstance(bytes_obj, bytes):
            raise Exception("bytes_obj必须为bytes类型")
        # 原始数据的长度
        obj_length = len(bytes_obj)
        if obj_length == 0:
            raise Exception("不能发送空值")
        # 计算原始数据的md5
        obj_hash = MyMD5.encrypt(bytes_obj)
        # 描述信息，即MD5|SIZE
        desc = "%s|%d" % (obj_hash, obj_length)
        if not self.conn:
            raise Exception("当前没有连接")
        try:
            # 发送md5和长度
            self.conn.send(desc.encode('utf8'))
            # 接收方确认开始
            self.conn.recv(1024)
            # 开始发送原始数据
            self.conn.send(bytes_obj)
        except Exception as e:
            print(e)
            return False

    def recv(self):
        """
        接收方封装方法，先接收一个关于原始数据的md5和长度
        确认后，再接收原始数据
        :return:
        """
        raw_data = self.conn.recv(1024)
        if not raw_data:
            return False
        return raw_data
        # if not self.conn:
        #     raise Exception("当前没有连接")
        # # 接收md5和长度
        # raw_data = self.conn.recv(1024)
        # if not raw_data:
        #     return False
        # desc = raw_data.decode('utf8')
        # obj_hash = desc.split('|')[0]
        # obj_size = desc.split('|')[1]
        # self.conn.send(b'ACK')
        # received_size = 0
        # received_data = b''
        # while received_size < obj_size:
        #     tmp_data = self.conn.recv(1024)
        #     received_data += tmp_data
        #     received_size += len(tmp_data)
        # return received_data




if __name__ == '__main__':
    f = Ftp()
    f.send(b'123')