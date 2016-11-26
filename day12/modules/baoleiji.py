#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : baoleiji.py
from day12.modules.tables import *
import hashlib, yaml


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
        ret = list([g.id for g in whole_list])
        return ret

    @staticmethod
    def create_host_user(auth_user, using_key, auth_pass="", auth_key=""):
        """
        创建主机上的用户认证信息
        :param auth_user:
        :param using_key:
        :param auth_pass:
        :param auth_key:
        :return:
        """
        hu_obj = HostUser(auth_user=auth_user, using_key=using_key, auth_pass=auth_pass, auth_key=auth_key)
        session.add(hu_obj)
        session.commit()
        return hu_obj.id

    @staticmethod
    def create_users(user_list: list):
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
        ret = []
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
            ret.append(uid)
            if gid_list:
                for gid in gid_list:
                    user2group_obj = User2Group(uid=uid, gid=gid)
                    session.add(user2group_obj)
                session.commit()
            else:
                print(name, "用户已经添加，但没有加入任何的组")
        return ret

    @staticmethod
    def create_host(hostname, ip, port):
        """
        创建主机
        :param port: 数字
        :param hostname: 字符串
        :param ip: 字符串
        :return:
        """
        if not hostname.strip():
            raise Exception("主机名不能为空")
        host_exsit = Baoleiji.load_host(hostname)
        if host_exsit:
            ret = host_exsit.id
        else:
            host_obj = Host(name=hostname, ip=ip, port=port)
            session.add(host_obj)
            session.commit()
            ret = host_obj.id
        return ret

    @staticmethod
    def host2hostgroups(hid, hgid):
        h2hg_obj = Host2HostGroup(hid=hid, hgid=hgid)
        session.add(h2hg_obj)
        session.commit()

    @staticmethod
    def load_user_group(groupname: str):
        return session.query(UserGroup).filter(UserGroup.name == groupname).first()

    @staticmethod
    def load_host_group(groupname: str):
        return session.query(HostGroup).filter(HostGroup.name == groupname).first()

    @staticmethod
    def load_user(username: str):
        return session.query(User).filter(User.name == username).first()

    @staticmethod
    def load_host(hostname: str):
        return session.query(Host).filter(Host.name == hostname).first()




if __name__ == '__main__':
    print(Baoleiji.load_user_group("admi1n"))
    print(Baoleiji.load_host_group("wwww"))