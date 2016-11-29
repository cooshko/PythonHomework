#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : baoleiji.py
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)
from day12.modules.tables import *
import hashlib, yaml, sqlalchemy


class Baoleiji(object):
    @staticmethod
    def create_user_groups(user_groups: list):
        """
        创建用户组
        :param user_groups:example: [{group1: name, desc: description}, {group2: name, desc: description}]
        :return:
        """
        for g in user_groups:
            ug_obj = UserGroup(name=g.get('name'), description=g.get('description'))
            Baoleiji.session_add(ug_obj)

    @staticmethod
    def create_host_groups(host_groups: list):  # example参考上面
        """
        创建主机组
        :param host_groups:
        :return:
        """
        # whole_list = []
        ret = []
        for g in host_groups:
            group_exist = Baoleiji.load_host_group(g['name'])
            if group_exist:
                ret.append(group_exist.id)
            else:
                group_obj = HostGroup(name=g['name'], description=g['description'])
                Baoleiji.session_add(group_obj)
                ret.append(group_obj.id)
        #     whole_list.append(HostGroup(name=g['name'], description=g['description']))
        # session.add_all(whole_list)  # 使用add_all减少数据库交换
        # session.commit()
        # ret = list([g.id for g in whole_list])
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
        Baoleiji.session_add(hu_obj)
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
                    Baoleiji.session_add(user2group_obj)
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
            Baoleiji.session_add(host_obj)
            ret = host_obj.id
        return ret

    @staticmethod
    def host2hostgroups(hid, hgid):
        """
        主机加入到主机组
        :param hid:
        :param hgid:
        :return:
        """
        h2hg_obj = Host2HostGroup(hid=hid, hgid=hgid)
        ret = Baoleiji.session_add(h2hg_obj)
        return ret

    @staticmethod
    def host2hostuser(hid, huid):
        """
        创建主机对应的用户认证，它们的关系是多台主机共享一个用户认证方法
        :param hid:
        :param huid:
        :return:
        """
        h2hu_obj = Host2HostUser(hid=hid, huid=huid)
        ret = Baoleiji.session_add(h2hu_obj)
        return ret

    @staticmethod
    def user2host2hostuser(uid, hid, hgid, huid):
        """
        建立堡垒机用户-主机-主机用户的管理
        :param hgid:
        :param uid:
        :param hid:
        :param huid:
        :return:
        """
        obj = User2Host2HostUser(uid=int(uid), hid=int(hid), hgid=int(hgid), huid=int(huid))
        ret = Baoleiji.session_add(obj)
        return ret

    @staticmethod
    def load_user_group(groupname: str):
        return session.query(UserGroup).filter(UserGroup.name == groupname).first()

    @staticmethod
    def load_host_group(groupname: str):
        return session.query(HostGroup).filter(HostGroup.name == groupname).first()

    @staticmethod
    def session_add(obj):
        try:
            session.add(obj)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False

    @staticmethod
    def load_all_host_groups():
        groups_obj_list = session.query(HostGroup).all()
        return list([{
                         'gid': group.id,
                         'groupname': group.name,
                         'description': group.description,
                         'hosts': list([{
                                   'hid': host.id,
                                   'hostname': host.name,
                                   'auth_users': list({
                                                          'auth_user_id': hu.id,
                                                          'auth_user': hu.auth_user
                                                      } for hu in host.host_user)
                                }for host in group.host])
                    } for group in groups_obj_list])

    @staticmethod
    def user_manage_group(username: str, groupname: str, role: str, leave=False):
        """
        根据组名来管理一组主机
        :param role: 角色，即主机上的用户
        :param username: 堡垒机的用户名
        :param groupname: 主机组名
        :return:
        """
        user = session.query(User).filter(User.name == username).first()
        host_group = session.query(HostGroup).filter(HostGroup.name == groupname).first()
        auth_user = session.query(HostUser).filter(HostUser.auth_user == role).first()
        if user and host_group and auth_user:
            # 如果三者均存在，检查该主机组的主机是否拥有相关的主机用户
            if leave:
                # 如果是取消管理主机组
                session.query(User2Host2HostUser) \
                    .filter(User2Host2HostUser.uid == user.id,
                            User2Host2HostUser.hgid == host_group.id,
                            User2Host2HostUser.huid == auth_user.id) \
                    .delete()
                session.commit()
                return True
            else:
                # 堡垒机用户管理主机组
                has_host_user = session.query(Host2HostUser)\
                    .filter(Host2HostUser.hid == host_group.host[0].id,
                            Host2HostUser.huid == auth_user.id).first()
                if has_host_user:
                    # 如果该主机对应有这个主机用户
                    for host in host_group.host:
                        obj = User2Host2HostUser(uid=user.id, hid=host.id, hgid=host_group.id, huid=auth_user.id)
                        Baoleiji.session_add(obj)
                    return True
                else:
                    return False
        else:
            return False

    @staticmethod
    def user_manage_host(username: str, hostgroup:str, hostname: str, role: str, leave=False):
        """
        根据主机名来管理特定主机
        :param groupname:
        :param username: 堡垒机用户
        :param hostname: 主机名
        :param role: 角色
        :return:
        """
        user = session.query(User).filter(User.name == username).first()
        host = session.query(Host).filter(Host.name == hostname).first()
        group = session.query(HostGroup).filter(HostGroup.name == hostgroup).first()
        auth_user = session.query(HostUser).filter(HostUser.auth_user == role).first()
        if user and host and group and auth_user:
            # 四者均存在
            if leave:
                # 堡垒机用户不再拥有特定主机的特定账户
                session.query(User2Host2HostUser).filter(User2Host2HostUser.uid == user.id,
                                                         User2Host2HostUser.hid == host.id,
                                                         User2Host2HostUser.hgid == group.id,
                                                         User2Host2HostUser.huid == auth_user.id)\
                                                 .delete()
                session.commit()
                return True
            else:
                has_host_user = session.query(Host2HostUser)\
                    .filter(Host2HostUser.hid == host.id,
                            Host2HostUser.huid == auth_user.id).first()
                host_in_hostgroup = session.query(Host2HostGroup).filter(Host2HostGroup.hgid == group.id,
                                                                         Host2HostGroup.hid == host.id).first()
                if has_host_user and host_in_hostgroup:
                    # 如果主机上有对应的主机用户，那么关联到堡垒机用户
                    obj = User2Host2HostUser(uid=user.id, hid=host.id, huid=auth_user.id, hgid=group.id)
                    Baoleiji.session_add(obj)
                    return True
                else:
                    return False
        else:
            return False

    @staticmethod
    def load_user_info(username: str, password: str):
        """
        堡垒机用户认证，除了用户名密码外，认证过程中还会涉及用户是否enable
        :param username:
        :param password:
        :return: 返回当前用户能操纵的主机列表
        """
        m = hashlib.md5()
        m.update(password.encode())
        password_md5 = m.hexdigest()
        user = session.query(User).filter(User.name == username,
                                             User.password == password_md5,
                                             User.enable == True).first()
        if user:
            # 获取用户能操纵的主机列表
            # u2h2hu = session.query(User2Host2HostUser).filter(User2Host2HostUser.uid == user.id).all()
            host_groups = session.query(func.distinct(User2Host2HostUser.hgid))\
                .filter(User2Host2HostUser.uid == user.id).all()
            # print(host_groups)
            ret = dict()
            if host_groups:
                for hg in host_groups:
                    hgid = hg[0]
                    hg_name = session.query(HostGroup.name).filter(HostGroup.id == hgid).first().name
                    h2hu_by_hg = session.query(Host.name, Host.ip, Host.port, HostUser.auth_user,
                                               HostUser.using_key, HostUser.auth_pass, HostUser.auth_key)\
                        .filter(
                        User2Host2HostUser.uid == user.id,
                        User2Host2HostUser.hid == Host.id,
                        User2Host2HostUser.huid == HostUser.id,
                        User2Host2HostUser.hgid == hgid
                    ).all()
                    ret[hg_name] = h2hu_by_hg
                return ret
        else:
            # 认证失败
            return False

    @staticmethod
    def load_user(username: str):
        return session.query(User).filter(User.name == username).first()

    @staticmethod
    def load_host(hostname: str):
        return session.query(Host).filter(Host.name == hostname).first()

    @staticmethod
    def user_change_password(username: str,new_password: str):
        m = hashlib.md5()
        m.update(new_password.encode())
        new_password_md5 = m.hexdigest()
        session.query(User).filter(User.name == username).update({'password': new_password_md5})
        session.commit()

    @staticmethod
    def enable_user(username: str, enable: bool):
        session.query(User).filter(User.name == username).update({'enable': enable})
        session.commit()

    @staticmethod
    def resync_db():
        drop_db_tables()
        create_db_tables()

if __name__ == '__main__':
    # print(Baoleiji.load_user_group("admi1n"))
    # print(Baoleiji.load_host_group("wwww"))
    # print(Baoleiji.user_change_password("coosh", "coosh123"))
    Baoleiji.enable_user("coosh", True)