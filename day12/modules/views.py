#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : views.py
import sys
from day12.modules.tables import *
import hashlib


class Views(object):
    @staticmethod
    def create_user_groups(user_groups: list):  # example: [{group1: name, desc: description}, {group2: name, desc: description}]
        """
        创建用户组
        :param user_groups:
        :return:
        """
        whole_list = []
        for g in user_groups:
            whole_list.append(UserGroup(name=g['name'], description=g['description']))
        session.add_all(whole_list)     # 使用add_all减少数据库交换
        session.commit()

    @staticmethod
    def create_host_groups(host_groups: list):  # example参考上面
        """
        创建主机组
        :param host_groups:
        :return:
        """
        whole_list = []
        for g in host_groups:
            whole_list.append(HostGroup(name=g['name'], description=g['description']))
        session.add_all(whole_list)  # 使用add_all减少数据库交换
        session.commit()

    @staticmethod
    def create_user(user_list: list):  # example: [{username1: name, password: plainText}, {username2: name, password: plainText}]
        whole_list = []
        for u in user_list:
            name = u['name'].strip()
            m = hashlib.md5()
            m.update(u['password'])
            passwd_md5 = m.hexdigest()
            whole_list.append(User(name, passwd_md5))
        session.add_all(whole_list)
        session.commit()


if __name__ == '__main__':
    # 创建用户组
    # filepath = r"../samples/new_user_groups.txt"
    # with open(filepath) as fh:
    #     li = []
    #     for line in fh:
    #         try:
    #             name, desc = line.strip().split()
    #         except:
    #             name = line.strip()
    #             desc = ""
    #         li.append({
    #             "name": name,
    #             "description": desc
    #         })
    #     Views.create_user_groups(li)

    # 创建主机组
    # filepath = r"../samples/new_host_groups.txt"
    # with open(filepath, encoding="utf8") as fh:
    #     li = []
    #     for line in fh:
    #         try:
    #             name, desc = line.strip().split()
    #         except:
    #             name = line.strip()
    #             desc = ""
    #         li.append({
    #             "name": name,
    #             "description": desc
    #         })
    #     Views.create_host_groups(li)
    pass