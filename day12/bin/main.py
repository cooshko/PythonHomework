#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py.py
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)
from day12.modules.views import Views
TIPS = """
使用方法：
1) python3 main.py <首要命令> [-ughfr] [用户名|主机组|主机名|文件路径|角色]
2) python3 main.py interactive

首要命令：
add-user-groups -f filepath
add-host-groups -f filepath
add-users -f filepath
add-hosts -f filepath
reset-user-password -u user newpass
user-manage-host-group -u user -g hostgroup -r role
user-manage-host -u user -g hostgroup -h host -r role
user-leave-host-group -u user -g hostgroup -r role
user-leave-host -u user -g hostgroup -h host -r role
sync_db
interactive

参数：
-u 指定用户名
-g 主机组
-h 指定主机

用法举例：
coosh用户管理lab主机组所有主机
python3 main.py user-manage-host-group -u coosh -g lab
"""
# sys.argv.append("add-user-groups")
# sys.argv.append("-f")
# sys.argv.append("../sample/new_user_groups.txt")
if __name__ == '__main__':
    if len(sys.argv)>1:
        action = sys.argv[1]

        if action == "add-user-groups":
            # add-user-groups -f filepath
            index = sys.argv.index("-f")
            filepath = sys.argv[index + 1]
            Views.create_user_groups_from_file(filepath)

        elif action == "add-host-groups":
            # add-host-groups -f filepath
            index = sys.argv.index("-f")
            filepath = sys.argv[index + 1]
            Views.create_host_groups_from_file(filepath)

        elif action == "add-users":
            # add-users -f filepath
            index = sys.argv.index("-f")
            filepath = sys.argv[index + 1]
            Views.create_user_from_file(filepath)

        elif action == "add-hosts":
            # add-hosts -f filepath
            index = sys.argv.index("-f")
            filepath = sys.argv[index + 1]
            Views.create_host_from_file(filepath)

        elif action == "reset-user-password":
            # reset-user-password -u user newpass
            index = sys.argv.index("-u")
            user = sys.argv[index + 1]
            newpass = sys.argv[index + 2]
            Views.user_change_password(user, newpass)

        elif action == "user-manage-host-group":
            # user-manage-host-group -u user -g hostgroup -r role
            index = sys.argv.index("-u")
            user = sys.argv[index + 1]
            index = sys.argv.index("-g")
            hostgroup = sys.argv[index + 1]
            index = sys.argv.index("-r")
            role = sys.argv[index + 1]
            Views.user_manage_group(user, hostgroup, role)

        elif action == "user-manage-host":
            # user-manage-host -u user -h host -r role
            index = sys.argv.index("-u")
            user = sys.argv[index + 1]
            index = sys.argv.index("-h")
            host = sys.argv[index + 1]
            index = sys.argv.index("-g")
            group = sys.argv[index + 1]
            index = sys.argv.index("-r")
            role = sys.argv[index + 1]
            Views.user_manage_host(user, host, group, role)

        elif action == "user-leave-host-group":
            # user-leave-host-group -u user -g hostgroup -r role
            index = sys.argv.index("-u")
            user = sys.argv[index + 1]
            index = sys.argv.index("-g")
            hostgroup = sys.argv[index + 1]
            index = sys.argv.index("-r")
            role = sys.argv[index + 1]
            Views.user_manage_group(user, hostgroup, role, leave=True)

        elif action == "user-leave-host":
            # user-leave-host -u user -h host -r role
            index = sys.argv.index("-u")
            user = sys.argv[index + 1]
            index = sys.argv.index("-h")
            host = sys.argv[index + 1]
            index = sys.argv.index("-g")
            group = sys.argv[index + 1]
            index = sys.argv.index("-r")
            role = sys.argv[index + 1]
            Views.user_manage_host(user, host, group, role, leave=True)

        elif action == "sync-db":
            inp = input("这个操作会清空整个数据库，如确定请输入YES：")
            if inp == "YES":
                Views.sync_db()
            else:
                print("退出该操作")
        elif action == "interactive":
            Views.interactive()
    else:
        print(TIPS)
