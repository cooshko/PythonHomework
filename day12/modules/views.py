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

    @staticmethod
    def connect_user_host_hostuser():
        current_user = {"id":1, "name":"coosh"}
        menu = Baoleiji.load_all_host_groups()
        for group in menu:
            print(group[0], group[2])
        group_choice = int(input("请输入主机组：").strip())
        for host in menu[group_choice]:
            print(host[0], host[1])
        host_choice = int(input("请输入主机：").strip())
        for host_user in menu[group_choice][host_choice]:
            print(host_user[0], host_user[1])
        host_user_choice = int(input("请输入用户：").strip())

if __name__ == '__main__':
    # Views.create_user_groups_from_console()
    # Views.create_host_groups_from_console()
    # Views.create_user_from_console()
    # Views.create_host_from_sample()
    Views.connect_user_host_hostuser()
    pass
