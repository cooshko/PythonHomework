#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, socket, threading, chardet, re, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT)
from day10.libs.mylog import MyLog
from day10.libs.mytrans import MyTransMixIn


class Mfm(MyTransMixIn):
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = os.path.join(APP_DIR, 'log')
    CONF_DIR = os.path.join(APP_DIR, 'conf')

    def __init__(self, isdebug=False):
        self.isdebug = isdebug
        self.host_list = []
        self.group_dict = dict()
        log_file = os.path.join(Mfm.LOG_DIR, 'mfm.log')
        self.logger = MyLog(logfile=log_file, logconsole=isdebug)
        self.load_config()

    def auth(self, sock, username, password):
        """
        远程验证用户
        :param sock:
        :param username:
        :param password:
        :return:
        """
        m = hashlib.md5()
        m.update(password.encode())
        data = (username + "|" + m.hexdigest()).encode()
        MyTransMixIn.send_once(sock, data)
        resp = MyTransMixIn.recv_once(sock).decode()
        status, reason = resp.split("|", maxsplit=1)
        if status == "OKAY":
            return True
        else:
            return False

    def commander(self, node_ip, node_port, node_username, node_password, command, output_file=False):
        """
        具体与各被控节点交互的方法。输入依赖参数传递，结果一定会输出到命令行，也可以输出到文件
        :param node_password:
        :param node_username:
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
            # 连接上后，验证用户名、密码
            if not self.auth(sock, node_username, node_password):
                # 如果验证失败，打印消息并返回False
                sock.close()
                print(ip_info + "验证失败")
                self.logger.error(ip_info + "验证失败")
                return False
            # 判断一下，是执行命令还是上传下载命令
            if command.startswith("put "):
                # 上传命令
                local_file = command.replace("put ", "").strip()
                if os.path.isfile(local_file):
                    self.send_once(sock, command.encode())
                    success, desc = MyTransMixIn.send_file(sock, local_file)
                    self.logger.info(ip_info + "尝试发送文件：" + local_file)
                    if success:
                        cmd_result = "成功！"
                        self.logger.info(ip_info + "成功")
                    else:
                        cmd_result = "失败。" + desc
                else:
                    cmd_result = "失败。本地文件不存在"
            elif command.startswith("get "):
                # 下载命令
                filename = os.path.basename(command.replace("get ", "").strip())
                # 发一次命令给对端
                self.send_once(sock, command.encode())
                # 接收对端的确认消息
                # status, reason = self.recv_once(sock).decode().split("|", maxsplit=1)
                # 创建本地目录
                data_dir = os.path.join(self.APP_DIR, 'data', node_ip)
                if not os.path.isdir(data_dir):
                    os.mkdir(data_dir)
                # 本地目标路径
                file_path = os.path.join(data_dir, filename)
                success, desc = MyTransMixIn.recv_file(sock, data_dir)
                if success:
                    cmd_result = "成功！文件保存到 " + file_path
                else:
                    cmd_result = "失败。原因：" + desc
                self.logger.info(ip_info + cmd_result)
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
        finally:
            sock.close()

    def output_file(self, ip, msg):
        # 把回显结果写到对应的ip文件中
        of = os.path.join(Mfm.LOG_DIR, ip + '.txt')
        with open(of, 'a', encoding='utf-8') as f:
            f.write(msg)

    def load_config(self):
        """
        重新读取配置文件，重置组列表和主机列表
        :return:
        """
        self.host_list = []
        self.group_dict = dict()
        hosts_conf = os.path.join(Mfm.CONF_DIR, 'hosts.cfg')
        with open(hosts_conf) as f:
            for line in f:
                if line.startswith("#"):
                    # 忽略以井号开头的内容
                    continue
                hostname, url, group = line.split()
                username, password, ip, port = re.findall(r"(.+):(.*)@(.+):(\d+)", url)[0]
                host = {'hostname': hostname,
                        'ip': ip,
                        'port': int(port),
                        'username': username,
                        'password': password, }
                if group in self.group_dict:
                    self.group_dict[group].append(host)
                else:
                    self.group_dict[group] = [host]
                self.host_list.append(host)

    def list_hosts(self):
        # 显示所有主机信息
        print("总共%d个主机" % len(self.host_list))
        for host in self.host_list:
            print("%10s %s:%d %s %s" % (host["hostname"], host['ip'], host['port'], host['username'], host['password']))

    def display_groups(self):
        # 显示组的信息
        print("共%d组" % len(self.group_dict))
        for group_name in self.group_dict:
            print(group_name, "组")
            for host in self.group_dict[group_name]:
                print("%10s %s:%d %s %s" % (
                host["hostname"], host['ip'], host['port'], host['username'], host['password']))

    def display_help(self):
        print("""
{scriptname:s} [option] ["command"]
OPTIONS:
--list  查看主机列表
--groups 查看组
-H <"command"> 对所有主机执行命令
-G GROUPNAME <"command"> 对指定组的所有主机执行命令

COMMANDS:
get REMOTE-FILE-PATH 尝试获取远程主机指定路径的文件
put LOCAL-FILE-PATH  将本地文件上传到远程主机
其他指令直接发往远程主机上执行
            """.format(scriptname=sys.argv[0]))

    def router(self):
        """
        根据命令行参数，执行不同的任务
        :return:
        """
        if "--help" in sys.argv:
            self.display_help()
        elif "--list" in sys.argv:
            self.list_hosts()
        elif "--groups" in sys.argv:
            self.display_groups()
        elif "-H" in sys.argv:
            # 对全部主机执行指令
            self.load_config()
            position = sys.argv.index("-H")
            command = sys.argv[position+1]
            for host in self.host_list:
                t = threading.Thread(target=self.commander, kwargs={'node_ip': host['ip'],
                                                                    'node_port': host['port'],
                                                                    'node_username': host['username'],
                                                                    'node_password': host['password'],
                                                                    'command': command,
                                                                    'output_file': True
                                                                    })
                t.start()

        elif "-G" in sys.argv:
            # 仅对组成员执行指令
            self.load_config()
            position = sys.argv.index("-G")
            group_name = sys.argv[position+1].strip()
            command = sys.argv[position+2]
            if group_name in self.group_dict:
                for host in self.group_dict[group_name]:
                    t = threading.Thread(target=self.commander, kwargs={'node_ip': host['ip'],
                                                                        'node_port': host['port'],
                                                                        'node_username': host['username'],
                                                                        'node_password': host['password'],
                                                                        'command': command,
                                                                        'output_file': True
                                                                        })
                    t.start()
            else:
                print("没有这个组，请使用 --groups 选项查看")
        else:
            self.display_help()

if __name__ == '__main__':
        mfm = Mfm(isdebug=True)
        mfm.router()
