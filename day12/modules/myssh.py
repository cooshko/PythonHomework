#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime, paramiko, socket, logging, json, types
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(APP_ROOT)
LOG_DIR = os.path.join(APP_ROOT, 'log')
DATA_DIR = os.path.join(APP_ROOT, 'data')

# windows does not have termios...
try:
    import termios
    import tty

    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False


# 日志装饰器函数
FF = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%F %H:%M:%S")
FH = logging.FileHandler(filename=os.path.join(LOG_DIR, "access.log"), encoding="utf-8")
FH.setLevel(logging.DEBUG)
FH.setFormatter(FF)
LOGGER = logging.getLogger('ACCESS-LOG')
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(FH)
def log_access(func):
    def wrapper(*args, **kwargs):
        myssh = args[0]
        # args_str = json.dumps(args[1:])
        # kwargs_str = json.dumps(kwargs)
        args_for_log = []
        for arg in args[1:]:
            if not isinstance(arg, types.FunctionType):
                args_for_log.append(arg)
        kwargs_for_log = dict()
        for key in kwargs:
            if not isinstance(kwargs[key], types.FunctionType):
                kwargs_for_log[key] = kwargs[key]
        args_str = json.dumps(args_for_log)
        kwargs_str = json.dumps(kwargs_for_log)
        log_msg = "%s on %s %s %s" % (myssh.user, myssh.hostname, func.__name__, args_str + kwargs_str)
        LOGGER.info(log_msg)
        ret = func(*args, **kwargs)
        return ret
    return wrapper


class MySSH(object):
    FF = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%F %H:%M:%S")
    FH = logging.FileHandler(filename=os.path.join(LOG_DIR, "cmd.log"), encoding="utf-8")
    FH.setLevel(logging.DEBUG)
    FH.setFormatter(FF)
    LOGGER = logging.getLogger('CMD-LOG')
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(FH)

    def __init__(self, user, hostname, port, ssh_user, using_key, passwd, pkey_file):
        self.user = user
        self.hostname = hostname
        self.port = port
        self.ssh_user = ssh_user
        self.ssh_pass = passwd
        self.ssh_key = pkey_file
        self.using_key = using_key
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.using_key:
            try:
                pkey = paramiko.RSAKey.from_private_key_file(self.ssh_key)
            except paramiko.ssh_exception.PasswordRequiredException as e:
                while True:
                    try:
                        key_pass = input("KEY文件加密了，请输入密码：")
                        pkey = paramiko.RSAKey.from_private_key_file(self.ssh_key, key_pass)
                        break
                    except paramiko.ssh_exception.SSHException as e:
                        print("密码错，请重新输入")

            self.client.connect(hostname=self.hostname,
                                port=self.port,
                                username=self.ssh_user,
                                pkey=pkey)
        else:
            self.client.connect(hostname=self.hostname,
                                port=self.port,
                                username=ssh_user,
                                password=self.ssh_pass)
        self.chan = self.client.invoke_shell()
        t = self.client.get_transport()
        self.sftp_client = paramiko.SFTPClient.from_transport(t)

    def excute_command(self, cmd, callback):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        out = stdout.read()
        err = stderr.read()
        b_ret = out if out else err
        import chardet
        charset = chardet.detect(b_ret)['encoding']
        ret = b_ret.decode(encoding=charset)
        callback(self.hostname, ret)


    def interactive_shell(self):
        if HAS_TERMIOS:
            self.posix_shell()
        else:
            self.windows_shell()

    def posix_shell(self):
        import select
        # chan = self.client.invoke_shell()
        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            self.chan.settimeout(0.0)

            cmd = ""
            tab_flag = False
            while True:
                r, w, e = select.select([self.chan, sys.stdin], [], [])
                if self.chan in r:
                    try:
                        x = self.chan.recv(10240).decode()
                        if len(x) == 0:
                            sys.stdout.write('\r\n*** EOF\r\n')
                            break
                        if tab_flag:
                            if "\r" not in x:
                                cmd += x
                            tab_flag = False
                        sys.stdout.write(x)
                        sys.stdout.flush()
                    except socket.timeout:
                        pass
                if sys.stdin in r:
                    x = sys.stdin.read(1)
                    if len(x) == 0:
                        break
                    elif x == "\r":
                        self.log_cmd(cmd)
                        cmd = ""
                    elif x == "\b":
                        cmd = cmd[:-1]
                    elif x == "\t":
                        tab_flag = True
                    else:
                        cmd += x
                    self.chan.send(x)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

    def log_cmd(self, cmd):
        # 记录用户执行过的命令
        # print("-->", cmd)
        log_msg = "%s: %s" % (self.user, str(cmd))
        MySSH.LOGGER.info(log_msg)

    def windows_shell(self):
        import threading

        sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")

        def writeall(sock):
            while True:
                data = sock.recv(256).decode()
                if not data:
                    sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                    sys.stdout.flush()
                    break
                sys.stdout.write(data)
                sys.stdout.flush()

        writer = threading.Thread(target=writeall, args=(self.chan,))
        writer.start()

        try:
            while True:
                d = sys.stdin.read(1)
                if not d:
                    break
                self.chan.send(d)
        except EOFError:
            # user hit ^Z or F6
            pass
        except OSError:
            pass

    @log_access
    def upload_file(self, local_file, remote_path, callback):
        """
        上传文件
        :param filepath:
        :return:
        """
        # t = self.client.get_transport()
        # sftp_client = paramiko.SFTPClient.from_transport(t)
        filename = os.path.basename(local_file)
        if r"/" in remote_path:
            # linux类的远程主机
            if remote_path[-1] == r"/":
                remote_file = remote_path + filename
            else:
                remote_file = remote_path + r"/" + filename
        else:
            # windows类
            if remote_path[-1] == "\\":
                remote_file = remote_path + filename
            else:
                remote_file = remote_path + "\\" + filename
        if os.path.isfile(local_file):
            try:
                ret = self.sftp_client.put(local_file, remote_file)
            except:
                # 远程路径不存在
                callback(self.hostname, "远程路径不存在")
        else:
            callback(self.hostname, "本地文件不存在")

    @log_access
    def download_file(self, remote_file, callback, toplevel_dir="by_host", secondary_dir="."):
        """
        下载文件
        :param secondary_dir: 如果是按组下载，则再却分来自哪个组
        :param toplevel_dir: 下载到本地后，存到指定目录，但要区分是按组还是按主机来下载
        :param remote_file: 远程文件路径
        :return:
        """
        filename = os.path.basename(remote_file)
        local_dir = os.path.join(DATA_DIR, toplevel_dir, secondary_dir)
        # if not os.path.isdir(local_dir):
        os.makedirs(name=local_dir, exist_ok=True)
        local_file = os.path.join(local_dir, filename)
        try:
            self.sftp_client.get(remote_file, local_file)
            return True
        except FileNotFoundError:
            callback(self.hostname, "文件不存在")

if __name__ == '__main__':
    ms = MySSH("coosh", "192.168.5.138", 22, "root", False, "24559982", "")
    # ms = MySSH("192.168.5.41", 22, "coosh", True, "", r"C:\Users\Coosh\Documents\Identity")
    # ms.interactive_shell()
    ms.upload_file(local_file=r"e:\test.txt", remote_path=r"/tmp")
    # ms.download_file(r"/tmp/test.txt")