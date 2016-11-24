#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : baoleiji.py
from day12.modules.tables import *
import hashlib


class Baoleiji(object):
    @staticmethod
    def create_user_groups(user_groups: list):
        """
        创建用户组
        :param user_groups:example: [{group1: name, desc: description}, {group2: name, desc: description}]
        :return:
        """
        whole_list = []
        for g in user_groups:
            whole_list.append(UserGroup(name=g['name'], description=g['description']))
        session.add_all(whole_list)  # 使用add_all减少数据库交换
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
    def create_user(user_list: list):
        """
        创建堡垒机用户
        :param user_list:
        example: [{
            username: name1,
            password: plainText,
            groups:[group1, group2]
        }, ]
        :return:
        """
        for u in user_list:
            name = u['username'].strip()
            m = hashlib.md5()
            m.update(u['password'].encode())
            passwd_md5 = m.hexdigest()
            groups = u['groups']
            if Baoleiji.load_user(name):
                print(name, "已经存在，不能重复创建")
                continue
            gid_list = []
            for group in groups:
                group_obj = Baoleiji.load_user_group(group)
                if group_obj:
                    gid_list.append(group_obj.id)
                else:
                    print(group, "组不存在")
            user_obj = User(name=name, password=passwd_md5, enable=True)
            session.add(user_obj)
            session.commit()
            uid = user_obj.id
            if gid_list:
                for gid in gid_list:
                    user2group_obj = User2Group(uid=uid, gid=gid)
                    session.add(user2group_obj)
                session.commit()
            else:
                print(name, "用户已经添加，但没有加入任何的组")

    @staticmethod
    def load_user_group(groupname: str):
        return session.query(UserGroup).filter(UserGroup.name == groupname).first()

    @staticmethod
    def load_host_group(groupname: str):
        return session.query(HostGroup).filter(HostGroup.name == groupname).first()

    @staticmethod
    def load_user(username: str):
        return session.query(User).filter(User.name == username).first()


if __name__ == '__main__':
    print(Baoleiji.load_user_group("admi1n"))
    print(Baoleiji.load_host_group("wwww"))