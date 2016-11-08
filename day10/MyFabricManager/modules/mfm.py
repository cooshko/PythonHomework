#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, socket, threading, chardet, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT)
from day10.libs.mylog import MyLog
from day10.libs.mytrans import MyTransMixIn


class Mfm(MyTransMixIn):
    def __init__(self, isdebug=False):
        self.isdebug = isdebug
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log')
        log_file = os.path.join(self.log_dir, 'mfm.log')
        self.logger = MyLog(logfile=log_file, logconsole=isdebug)

    def commander(self, node_ip, node_port, command, output_file=False):
        """
        具体与各被控节点交互的方法。输入依赖参数传递，结果一定会输出到命令行，也可以输出到文件
        :param output_file: 是否输出到文件
        :param node_ip: 节点ip地址
        :param node_port: 节点端口
        :param command: 发送给节点的命令
        :return:
        """
        command = command.strip()
        ip_info = ("[%s:%d] " % (node_ip, node_port))
        cmd_result = ""
        sock = socket.socket()
        try:
            sock.connect((node_ip, node_port))
            # 判断一下，是执行命令还是上传下载命令
            if command.startswith("put "):
                # 上传命令
                local_file = command.replace("put ", "").strip()
                if os.path.isfile(local_file):
                    self.send_once(sock, command.encode())
                    success, desc = MyTransMixIn.send_file(sock, local_file)
                    self.logger.info("尝试发送文件：" + local_file)
                    if success:
                        cmd_result = "成功！"
                        self.logger.info("成功")
                    else:
                        cmd_result = "失败。" + desc
                else:
                    cmd_result = "失败。本地文件不存在"
            elif command.startswith("get "):
                # 下载命令
                cmd_result = ''
            else:
                # 普通执行命令
                MyTransMixIn.send_once(sock, bytes(command, encoding="utf-8"))
                rsp = MyTransMixIn.recv_once(sock)
                # 为了能跨平台，编码交由chardet判断
                charset = chardet.detect(rsp)['encoding']
                cmd_result = rsp.decode(encoding=charset)
            # 关闭连接
            sock.close()
            whole_msg = "===START===\n{ip:s} >>> {cmd:s}\n{result:s}\n===END===\n".format(ip=ip_info,
                                                                                          cmd=command,
                                                                                          result=cmd_result)
            print(whole_msg)
            if output_file:
                self.output_file(node_ip, whole_msg)
        except Exception as e:
            self.logger.error(ip_info + str(e))
            raise
        finally:
            sock.close()

    def output_file(self, ip, msg):
        of = os.path.join(self.log_dir, ip + '.txt')
        with open(of, 'a', encoding='utf-8') as f:
            f.write(msg)

if __name__ == '__main__':
        mfm = Mfm(isdebug=True)
        mfm.commander("127.0.0.1", 9999, r"put F:\香港空运改造进度.xlsx", output_file=True)
