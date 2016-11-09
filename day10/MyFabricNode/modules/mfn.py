#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : mfn.py

import socket,os,sys,subprocess,configparser
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT)
from day10.libs.mylog import MyLog
from day10.libs.mytrans import MyTransMixIn


class Mfn(MyTransMixIn):
    def __init__(self, debug=False):
        """:param debug:是否调试模式"""
        self.conn = None
        self.addr = None
        self.setting = None
        self.debug = debug
        self.sock = socket.socket()
        logfile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log', 'access.log')
        self.logger = MyLog(logfile=logfile, logconsole=debug)
        # 读取配置文件
        conf_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf', 'mfn.conf')
        cp = configparser.ConfigParser()
        cp.read(conf_file)
        self.listen_ip = cp['global']['listen_ip']
        self.listen_port = int(cp['global']['listen_port'])
        self.username = cp['global']['username']
        self.password_md5 = cp['global']['password_md5']

    def auth(self):
        """
        验证用户
        :return:
        """
        raw_data = self.recv_once(self.conn)
        username, password_md5 = raw_data.decode().split("|", maxsplit=1)
        if username == self.username and password_md5 == self.password_md5:
            # 验证通过
            self.send_once(self.conn, "OKAY|验证通过".encode())
            self.logger.info(self.addr + "验证通过")
            return True
        else:
            # 验证失败
            self.send_once(self.conn, "NO|验证失败".encode())
            self.logger.info(self.addr + "验证失败")
            return False

    def run(self):
        # 监听指定端口
        self.sock.bind((self.listen_ip, self.listen_port))
        self.sock.listen(5)
        self.logger.info("服务启动")
        while True:
            self.conn, addr = self.sock.accept()
            self.addr = str(addr)
            self.logger.info(self.addr + "已连接")
            while True:
                try:
                    if not self.auth():
                        # 连接后，如果验证不通过，则中断连线
                        self.conn.close()
                        break
                    command_msg = MyTransMixIn.recv_once(self.conn).decode().strip()
                    if not command_msg:
                        raise Exception
                except Exception as e:
                    self.conn.close()
                    self.logger.error(str(addr) + str(e))
                    break
                self.logger.info(str(addr) + "发来指令：" + command_msg)
                cmd = command_msg.split(maxsplit=1)[0]
                args = command_msg.replace(cmd, "")
                if hasattr(self, "cmd_"+cmd):
                    # 对于特殊命令，在类中定义了方法的，由类方法执行处理
                    func = getattr(self, "cmd_"+cmd)
                    func(args)
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
        MyTransMixIn.send_file(self.conn, args[0])


if __name__ == '__main__':
    mfn = Mfn(True)
    mfn.run()