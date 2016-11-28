#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : views.py
import sys, yaml, os, getpass, paramiko
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)
from day12.modules.baoleiji import Baoleiji
from day12.modules.myssh import MySSH


class Views(object):
    baoleiji = Baoleiji()

    @staticmethod
    def create_user_groups_from_console():
        """
        创建堡垒机用户组
        :return:
        """
        filepath = r"../samples/new_user_groups.txt"
        with open(filepath, encoding="utf8") as fh:
            li = []
            for line in fh:
                try:
                    name, desc = line.strip().split()
                except:
                    name = line.strip()
                    desc = ""
                li.append({
                    "name": name,
                    "description": desc
                })
        Views.baoleiji.create_user_groups(li)

    @staticmethod
    def create_host_groups_from_sample():
        """
        创建主机组
        :return:
        """
        filepath = r"../samples/new_host_groups.txt"
        with open(filepath, encoding="utf8") as fh:
            li = []
            for line in fh:
                try:
                    name, desc = line.strip().split()
                except:
                    name = line.strip()
                    desc = ""
                li.append({
                    "name": name,
                    "description": desc
                })
        Views.baoleiji.create_host_groups(li)

    @staticmethod
    def create_user_from_console():
        filepath = r"../samples/new_users.txt"
        user_list = []
        with open(filepath, encoding="utf8") as fh:
            for line in fh:
                if line.strip():
                    username = line.split()[0]
                    password = line.split()[1]
                    groups = line.split()[2:]
                    user_list.append(
                        {
                            'username': username,
                            'password': password,
                            'groups': groups
                        }
                    )
        Baoleiji.create_users(user_list)

    @staticmethod
    def create_host_from_sample():
        # filepath = r"../samples/new_hosts.txt"
        filepath = r"../samples/real_hosts.txt"

        with open(filepath) as fh:
            var = yaml.load(fh)
        for group in var:
            groupname = group['groupname']
            group_obj = Baoleiji.load_host_group(groupname)
            hgid = None
            if not group_obj:
                print(groupname, "主机组不存在，无法添加该组名下的主机。")
                continue
            else:
                hgid = group_obj.id
            huid_list = []
            for hu in group['auth_set']:
                username = hu['user']
                using_key = True if "key" in hu else False
                password = str(hu.get("password", ""))

                key = hu.get('key', "")
                huid = Baoleiji.create_host_user(username, using_key, password, key)
                huid_list.append(huid)
            hid_list = []
            for host in group['hosts']:
                h = Baoleiji.load_host(host['name'])
                if h:
                    hid = h.id
                else:
                    hid = Baoleiji.create_host(host['name'], host['ip'], int(host['port']))
                hid_list.append(hid)
            if huid_list and hid_list:
                # 建立主机到认证方法和组的映射
                for hid in hid_list:
                    h2hg_obj = Baoleiji.host2hostgroups(hid=hid, hgid=hgid)
                    for huid in huid_list:
                        h2hu_obj = Baoleiji.host2hostuser(hid, huid)
        return True

    @staticmethod
    def interactive():
        # 清屏
        if os.name == "nt":
            os.system("cls")
        elif os.name == "posix":
            os.system("clear")
        while True:
            # 让用户输入认证信息
            while True:
                username = input("用户名：").strip()
                if username:
                    break
                else:
                    print("用户名不能为空")
            while True:
                # pycharm支持不是很好，先注释掉getpass
                # password = getpass.getpass(prompt="密码：").strip()
                password = input("密码：").strip()
                if password:
                    break
                else:
                    print("密码不能为空")

            # 开始读取用户信息，如果返回False，则代表用户名密码错
            info = Baoleiji.load_user_info(username, password)
            if info:
                while True:
                    # 认证通过会得到可以访问的主机信息
                    enum_info = enumerate(info, 1)
                    # 循环让用户选择要访问的主机
                    group_list = []
                    for key, g in enum_info:
                        group_list.append(g)
                        print(str(key)+")", g)
                    group_choice = int(input("\n请输入你要访问的组：").strip()) - 1
                    group_name = group_list[group_choice]
                    print("-->", group_name)
                    enum_host_info = enumerate(info[group_name], 1)
                    host_list = []
                    for key, host_info in enum_host_info:
                        host_list.append(host_info)
                        print(str(key)+")", host_info[0], host_info[3] + "@" + host_info[1])
                    host_choice = int(input("\n请输入你要访问的主机：").strip()) - 1
                    hostname, ip, port, auth_user, using_key, auth_pass, auth_key = host_info
                    myssh = MySSH(user=username, hostname=ip, port=port, ssh_user=auth_user, using_key=using_key,
                                  passwd=auth_pass, pkey_file=auth_key)
                    myssh.interactive_shell()
            else:
                print("用户名或密码不正确")


if __name__ == '__main__':
    # Views.create_user_groups_from_console()
    # Views.create_host_groups_from_sample()
    # Views.create_user_from_console()
    # Views.create_host_from_sample()
    sys.argv.append("--user")
    sys.argv.append("coosh")
    sys.argv.append("--manage")
    sys.argv.append("--group")
    sys.argv.append("www")
    sys.argv.append("--host")
    sys.argv.append("ubuntu")
    sys.argv.append("--role")
    sys.argv.append("mysql")
    # ret = Baoleiji.user_manage_group("coosh", "www", "nginx")
    # ret = Baoleiji.user_manage_group("coosh", "lab", "root")
    # ret = Baoleiji.user_manage_group("coosh", "production", "coosh")
    # ret = Baoleiji.user_manage_group("panny", "db", "mysql")
    # Baoleiji.user_manage_group("panny", "www", "nginx")
    # print(ret)
    # Baoleiji.load_user_info("coosh","coosh123")
    # Baoleiji.user_manage_group("panny", "ww", "nginx", leave=True)
    # Baoleiji.user_manage_host("panny", "www-mysql-1", "mysql", leave=True)
    # print(Baoleiji.load_user_info("panny", "panny123"))
    Views.interactive()
    pass
