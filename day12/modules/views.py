#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : views.py
import sys, yaml, os, getpass, paramiko, threading, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)
from day12.modules.baoleiji import Baoleiji
from day12.modules.myssh import MySSH


class Views(object):
    # baoleiji = Baoleiji()

    @staticmethod
    def create_user_groups_from_file(filepath):
        """
        创建堡垒机用户组
        :return:
        """
        # filepath = r"../samples/new_user_groups.txt"
        try:
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
            Baoleiji.create_user_groups(li)
        except Exception as e:
            print(e)

    @staticmethod
    def create_host_groups_from_file(filepath):
        """
        根据指定文件内容，创建主机组
        :return:
        """
        # filepath = r"../samples/new_host_groups.txt"
        try:
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
            Baoleiji.create_host_groups(li)
        except Exception as e:
            print(e)

    @staticmethod
    def create_user_from_file(filepath):
        """
        根据文件内容，创建多个用户
        :param filepath:
        :return:
        """
        # filepath = r"../samples/new_users.txt"
        user_list = []
        try:
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
        except Exception as e:
            print(e)

    @staticmethod
    def create_host_from_file(filepath):
        # filepath = r"../samples/new_hosts.txt"
        # filepath = r"../samples/real_hosts.txt"
        try:
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
        except Exception as e:
            print(e)

    @staticmethod
    def clear_screen():
        # 清屏
        if os.name == "nt":
            os.system("cls")
        elif os.name == "posix":
            os.system("clear")

    @staticmethod
    def interactive():
        Views.clear_screen()
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
                def result_output(h, result):
                    print("[%s]\n%s\n" % (h, result))
                while True:
                    # 认证通过会得到可以访问的主机信息
                    enum_info = enumerate(info, 1)
                    # 循环让用户选择要访问的主机
                    group_list = []
                    while True:
                        for key, g in enum_info:
                            group_list.append(g)
                            print(str(key)+")", g)
                        group_choice = int(input("\n请输入你要访问的组：").strip()) - 1
                        try:
                            group_name = group_list[group_choice]
                            break
                        except IndexError:
                            print("你的输入有误")
                            time.sleep(1)
                            continue
                    print("-->", group_name)
                    enum_host_info = enumerate(info[group_name], 1)
                    host_list = []
                    for key, host_info in enum_host_info:
                        host_list.append(host_info)
                        print(str(key)+")", host_info[0], host_info[3] + "@" + host_info[1])
                    print("\n选择主机或者输入[ g ]对该组主机操作")
                    host_choice = input(">> ").strip()
                    if host_choice == "g":
                        # 对组进行操作
                        print("对", group_name, "组进行的操作")
                        print("1) 上传文件\n2) 下载文件\n3) 执行一条命令\n")
                        user_choice = input(">> ").strip()
                        t_list = []
                        if user_choice == "1":
                            # 上传
                            local_file = input("本地文件的绝对路径：").strip()
                            if not os.path.isfile(local_file):
                                print("本地文件%s不存在" % local_file)
                                continue
                            remote_path = input("远程目录：").strip()
                            for hostname, ip, port, auth_user, using_key, auth_pass, auth_key in host_list:
                                myssh = MySSH(user=username, hostname=ip, port=port, ssh_user=auth_user,
                                              using_key=using_key, passwd=auth_pass, pkey_file=auth_key)
                                print("正在上传 %s 到 %s (%s) 的 %s" % (local_file, hostname, ip, remote_path))
                                t = threading.Thread(target=myssh.upload_file, kwargs={'local_file': local_file,
                                                                                       'remote_path': remote_path,
                                                                                       'callback': result_output})
                                t.start()
                                t_list.append(t)
                            for t in t_list:
                                t.join()
                            print("全部完毕")
                        elif user_choice == "2":
                            # 下载
                            remote_file = input("远程文件路径：").strip()
                            for hostname, ip, port, auth_user, using_key, auth_pass, auth_key in host_list:
                                myssh = MySSH(user=username, hostname=ip, port=port, ssh_user=auth_user,
                                              using_key=using_key, passwd=auth_pass, pkey_file=auth_key)
                                # myssh.download_file(toplevel_dir="by_group", secondary_dir=hostname)
                                print("正在下载 %s(%s) 的远程文件 %s" % (hostname,ip, remote_file))
                                t = threading.Thread(target=myssh.download_file, kwargs={"remote_file": remote_file,
                                                                                         "toplevel_dir": "by_group",
                                                                                         "secondary_dir": hostname,
                                                                                         "callback": result_output})
                                t.start()
                                t_list.append(t)
                            for t in t_list:
                                t.join()
                            print("全部完毕")
                        elif user_choice == "3":
                            # 执行一条命令并返回输出
                            cmd = input("请输入命令：").strip()
                            if cmd:
                                for hostname, ip, port, auth_user, using_key, auth_pass, auth_key in host_list:
                                    myssh = MySSH(user=username, hostname=ip, port=port, ssh_user=auth_user,
                                                  using_key=using_key, passwd=auth_pass, pkey_file=auth_key)
                                    t = threading.Thread(target=myssh.excute_command,
                                                         kwargs={'cmd': cmd, 'callback': result_output})
                                    t.start()
                                    t_list.append(t)
                                for t in t_list:
                                    t.join()
                            else:
                                print("空命令不能执行")
                        else:
                            print("你的选择有误")
                    else:
                        # 访问特定主机
                        host_choice = int(host_choice) - 1
                        try:
                            hostname, ip, port, auth_user, using_key, auth_pass, auth_key = host_list[host_choice]
                        except IndexError:
                            print("你的输入有误")
                            return
                        Views.clear_screen()
                        print("-->选择的是", hostname)
                        print("请选择：\n1) 访问shell\n2) 上传文件\n3) 下载文件\n")
                        user_choice = input(">> ").strip()
                        myssh = MySSH(user=username, hostname=ip, port=port, ssh_user=auth_user, using_key=using_key,
                                      passwd=auth_pass, pkey_file=auth_key)
                        Views.clear_screen()
                        if user_choice == "1":
                            myssh.interactive_shell()
                        elif user_choice == "2":
                            local_file = input("本地文件的绝对路径：").strip()
                            remote_path = input("要存放到远程主机的哪个目录？").strip()
                            if os.path.isfile(local_file):
                                print("上传中")
                                myssh.upload_file(local_file=local_file, remote_path=remote_path, callback=result_output)
                                print("上传完毕")
                            else:
                                print("本地文件不存在")
                        elif user_choice == "3":
                            # 对主机下载
                            remote_file = input("远程主机的文件绝对路径：").strip()
                            print("正在下载 %s(%s) 的 %s" % (hostname, ip, remote_file))
                            myssh.download_file(remote_file=remote_file, secondary_dir=hostname, callback=result_output)
                            print("下载完毕\n")

            else:
                print("用户名或密码不正确")

    @staticmethod
    def user_manage_group(username, groupname, role, leave=False):
        ret = Baoleiji.user_manage_group(username, groupname, role, leave)
        if ret:
            print("OK")
        else:
            print("失败，请检查用户或组是否存在")

    @staticmethod
    def user_manage_host(username, hostname, groupname, role, leave=False):
        ret = Baoleiji.user_manage_host(username, groupname, hostname, role, leave)
        if ret:
            print("OK")
        else:
            print("没有关联成功")

    @staticmethod
    def sync_db():
        Baoleiji.resync_db()

    @staticmethod
    def user_change_password(username, newpass):
        if Baoleiji.load_user(username):
            Baoleiji.user_change_password(username, newpass)
        else:
            print("该用户不存在")

    @staticmethod
    def enable_user(username, enable: bool):
        if Baoleiji.load_user(username):
            Baoleiji.enable_user(username, enable)

    @staticmethod
    def check_user_status(username):
        user = Baoleiji.load_user(username)
        if user:
            print("用户：", user.name)
            status = "有效" if user.enable else "无效"
            print("当前状态：", status)
        else:
            print("没有此用户")

    @staticmethod
    def check_host_group(groupname):
        group = Baoleiji.load_host_group(groupname)
        if group:
            print("存在")
        else:
            print("不存在")

if __name__ == '__main__':
    # Views.create_user_groups_from_file()
    # Views.create_host_groups_from_file()
    # Views.create_user_from_file()
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
    # Views.interactive()
    Baoleiji.user_manage_host("coosh", "production", "lab1", "coosh")
    pass
