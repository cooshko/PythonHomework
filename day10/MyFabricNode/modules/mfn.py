#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : mfn.py

import socket,logging,os,sys,subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT)
from day10.libs.mylog import MyLog
from day10.libs.mytrans import MyTransMixIn


class Mfn(MyTransMixIn):
    def __init__(self, debug=False):
        """:param debug:是否调试模式"""
        self.conn = None
        self.setting = None
        self.debug = debug
        self.sock = socket.socket()
        logfile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log', 'access.log')
        self.logger = MyLog(logfile=logfile, logconsole=debug)

    def run(self):
        self.sock.bind(("0.0.0.0", 9999))
        self.sock.listen(5)
        self.logger.info("服务启动")
        while True:
            self.conn, addr = self.sock.accept()
            self.logger.info(str(addr) + "已连接")
            while True:
                try:
                    command_msg = MyTransMixIn.recv_once(self.conn).decode().strip()
                    if not command_msg:
                        raise Exception
                except Exception as e:
                    self.logger.error(str(addr) + str(e))
                    break
                self.logger.info(str(addr) + "发来指令：" + command_msg)
                cmd = command_msg.split(maxsplit=1)[0]
                args = command_msg.replace(cmd, "")
                if hasattr(self, "cmd_"+cmd):
                    # 对于特殊命令，在类中定义了方法的，由类方法执行处理
                    func = getattr(self, "cmd_"+cmd)
                    func(args, conn=self.conn)
                else:
                    # 如非自定义方法，则交由操作系统执行
                    proc = subprocess.Popen(args=command_msg,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            shell=True)
                    res = proc.stdout.read()
                    err = proc.stderr.read()
                    if err:
                        rsp = err
                    elif res:
                        rsp = res
                    else:
                        rsp = b"DONE"
                    MyTransMixIn.send_once(self.conn, rsp)

    def cmd_put(self, *args, **kwargs):
        MyTransMixIn.recv_file(self.conn)

    def cmd_get(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    mfn = Mfn(True)
    mfn.run()