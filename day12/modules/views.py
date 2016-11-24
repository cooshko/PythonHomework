#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : views.py
import sys
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
        Baoleiji.create_user(user_list)


if __name__ == '__main__':
    # Views.create_user_groups_from_console()
    # Views.create_host_groups_from_console()
    Views.create_user_from_console()