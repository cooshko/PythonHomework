#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : views.py
import sys, yaml
from day12.modules.baoleiji import Baoleiji


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
    def create_host_groups_from_console():
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
        filepath = r"../samples/new_hosts.txt"
        with open(filepath) as fh:
            var = yaml.load(fh)
        for group in var:
            groupname = group['groupname']
            group_obj = Baoleiji.load_host_group(groupname)
            hgid = None
            if not group_obj:
                raise Exception(groupname, "不存在，无法继续。")
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

    # @staticmethod
    # def connect_user_host_hostuser():
    #     current_user = {"id":1, "name":"coosh"}
    #     menu = Baoleiji.load_all_host_groups()
    #     for key, group in enumerate(menu):
    #         print(key+1, group['groupname'])
    #     group_choice = menu[int(input("请输入主机组：").strip()) - 1]
    #     print("-->", group_choice['groupname'])
    #     for key, host in enumerate(group_choice['hosts']):
    #         print(key+1, host['hostname'])
    #     host_choice = group_choice['hosts'][int(input("请输入主机：").strip()) - 1]
    #     for key, host_user in enumerate(host_choice['auth_users']):
    #         print(key+1, host_user['auth_user'])
    #     host_user_choice = host_choice['auth_users'][int(input("请输入用户：").strip()) - 1]
    #     return host_user_choice


if __name__ == '__main__':
    # Views.create_user_groups_from_console()
    # Views.create_host_groups_from_console()
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
    # ret = Baoleiji.user_manage_group("panny", "db", "mysql")
    # Baoleiji.user_manage_group("panny", "www", "nginx")
    # print(ret)
    # Baoleiji.user_auth("coosh","coosh123")
    # Baoleiji.user_manage_group("panny", "ww", "nginx", leave=True)
    # Baoleiji.user_manage_host("panny", "www-mysql-1", "mysql", leave=True)
    print(Baoleiji.user_auth("panny", "panny123"))
    pass
