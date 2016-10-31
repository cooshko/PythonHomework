#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import socket


class Ftp(object):
    def __init__(self):
        self.sock = socket.socket()
        self.conn = None

    def send(self, byte_obj):
        pass

    def recv(self):
        pass
