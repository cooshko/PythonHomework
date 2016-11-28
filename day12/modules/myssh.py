#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime, paramiko, socket, logging
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(APP_ROOT)
LOG_DIR = os.path.join(APP_ROOT, 'log')

# windows does not have termios...
try:
    import termios
    import tty

    has_termios = True
except ImportError:
    has_termios = False


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

    def interactive_shell(self):
        if has_termios:
            self.posix_shell()
        else:
            self.windows_shell()

    def posix_shell(self):
        import select
        chan = self.client.invoke_shell()
        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            chan.settimeout(0.0)

            cmd = ""
            tab_flag = False
            while True:
                r, w, e = select.select([chan, sys.stdin], [], [])
                if chan in r:
                    try:
                        x = chan.recv(10240).decode()
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
                    chan.send(x)
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

        writer = threading.Thread(target=writeall, args=(chan,))
        writer.start()

        try:
            while True:
                d = sys.stdin.read(1)
                if not d:
                    break
                chan.send(d)
        except EOFError:
            # user hit ^Z or F6
            pass


if __name__ == '__main__':
    ms = MySSH("coosh", "192.168.5.138", 22, "root", False, "24559982", "")
    # ms = MySSH("192.168.5.41", 22, "coosh", True, "", r"C:\Users\Coosh\Documents\Identity")
    ms.interactive_shell()
