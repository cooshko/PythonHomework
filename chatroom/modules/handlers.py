#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime
import tornado.web
from tornado import gen
from sqlalchemy import func, and_, text
from sqlalchemy.orm import sessionmaker
from .session import session_factory
from .decorator import *
from .models import *
from .common import *


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        session_cls = session_factory()
        self.session = session_cls(self)
        DBSession = sessionmaker(bind=engine)
        self.db = DBSession()


class IndexHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if self.session['is_login']:
            self.redirect('/panel')
        else:
            self.render('index.html')


def verify_user(user, pwd):
    """
    验证用户合法性
    :param user:
    :param pwd:
    :return:
    """
    if user and pwd:
        pwd_md5 = md5(pwd+config.password_salt)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        user_obj = db_session.query(User).filter(
            and_(
                User.name == user,
                User.password == pwd_md5
            )
        ).first()
        return user_obj
    else:
        raise ValueError("请提供用户名密码")


class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.redirect('/')

    def post(self, *args, **kwargs):
        user = self.get_argument('user')
        pwd = self.get_argument('pwd')

        user_obj = verify_user(user, pwd)
        if user_obj:
            # 创建session
            self.session['is_login'] = True
            self.session['uid'] = user_obj.uid
            self.session['name'] = user_obj.name
            self.session['nickname'] = user_obj.nickname

            # 把用户登记到成员池
            MIB.register_member(user_obj.uid)

            # 返回结果给浏览器
            self.write(dict(status='ok', link='/panel'))
        else:
            self.write(dict(status='fail', error='用户名密码不正确'))


class RegisterHandler(BaseHandler):
    def post(self, *args, **kwargs):
        user = self.get_argument("new_user", None)
        pwd = self.get_argument("new_pwd", None)
        pwd2 = self.get_argument("pwd2", None)
        agreement = self.get_argument("agreement", None)

        if not agreement:
            self.write(dict(status='fail', error='阅读并同意用户协议才能注册'))
        elif pwd != pwd2:
            self.write(dict(status='fail', error='两次密码不一致'))
        elif not user:
            self.write(dict(status='fail', error='用户名不能为空'))
        elif not pwd:
            self.write(dict(status='fail', error='密码不能为空'))
        else:
            # 通过基本的检查
            Session = sessionmaker(bind=engine)
            session = Session()
            # 开始进入重复用户的检查
            count = session.query(func.count(User.uid)).filter(User.name == user).one()[0]

            if count == 0:
                """用户不存在，插入新数据"""
                new_user = User(name=user, password=md5(pwd+config.password_salt), nickname=user)
                session.add(new_user)
                session.commit()

                # 插入成功后，保存数据到session
                self.session['is_login'] = True
                self.session['uid'] = new_user.uid
                self.session['name'] = new_user.name
                self.session['nickname'] = new_user.nickname

                # 返回客户端结果
                self.write(dict(status='ok', link='/panel', uid=new_user.uid))
            else:
                self.write(dict(status='fail', error='用户名已存在'))


class PanelHandler(BaseHandler):
    @check_login
    def get(self, *args, **kwargs):
        self.render("panel.html", nickname=self.session['nickname'], uid=self.session['uid'])


class LogoutHandler(BaseHandler):
    def get(self, *args, **kwargs):
        session_id = self.get_cookie('session_id')
        if session_id:
            # 清理成员池
            current_user_id = self.session['uid']
            if current_user_id in MIB.member_pool:
                del MIB.member_pool[current_user_id]

            # 清理session对话
            self.session.destroy_session(session_id)
        self.write(dict(status='ok', link='/'))


class UserHandler(BaseHandler):
    def get(self, *args, **kwargs):
        name = self.get_argument('nickname', None)
        uid = self.get_argument('uid', None)
        if name:
            # 根据昵称查找用户信息
            # Session = sessionmaker(bind=engine)
            # db = Session()
            result = self.db.query(User.uid, User.nickname).filter(User.nickname == name).first()
            if result:
                uid, nickname = result
                self.write(dict(status='ok', data={'uid': uid, 'nickname': nickname}))
            else:
                self.write(dict(status='fail', error='查无此人'))
        elif uid:
            # 根据uid查找用户信息
            result = self.db.query(User.uid, User.nickname).filter(User.uid == int(uid)).first()
            if result:
                uid, nickname = result
                self.write(dict(status='ok', data={'uid': uid, 'nickname': nickname}))
            else:
                self.write(dict(status='fail', error='查无此人'))
        else:
            # 如果没有name
            pass


class FriendHandler(BaseHandler):
    @check_login_ajax
    def post(self, *args, **kwargs):
        new_friend_id = self.get_argument('new_friend_id')
        current_user_id = self.session['uid']
        if new_friend_id == str(current_user_id):
            self.write(dict(status='fail', error='不能添加自己'))
            return
        new_friend = self.db.query(User).filter(User.uid == new_friend_id).first()
        if new_friend:
            # current_user = self.db.query(User).filter(User.uid == current_user_id).first()
            count = self.db.query(Friends).filter(
                and_(
                    Friends.uid == current_user_id,
                    Friends.fid == new_friend_id
                )
            ).count()
            if count > 0:
                self.write(dict(status='fail', error='不能重复添加好友'))
                return
            self.db.add_all([
                Friends(uid=current_user_id, fid=new_friend_id),
                Friends(fid=current_user_id, uid=new_friend_id),
            ])
            self.db.commit()
            self.write(dict(status='ok'))
        else:
            self.write(dict(status='fail', error='此ID不存在'))

    @check_login_ajax
    def get(self, *args, **kwargs):
        """读取好友列表"""
        current_user_id = self.session['uid']
        all_friends = self.db.query(User.uid, User.nickname).filter(
            and_(
                User.uid == Friends.fid,
                Friends.uid == current_user_id,
            )
        ).all()
        self.write(dict(status='ok', friend_list=all_friends))

    @check_login_ajax
    def delete(self, *args, **kwargs):
        """删除好友"""
        print("in delete")


class ChatroomHandler(BaseHandler):
    @check_login_ajax
    def get(self, *args, **kwargs):
        """
        如果提交的有指定具体的聊天室id，返回聊天室信息
        :param args:
        :param kwargs:
        :return:
        """
        uid = self.session['uid']
        chatroom_id = self.get_argument('chatroom_id', None)
        ret = []
        if chatroom_id:
            chatroom_id = int(chatroom_id)
            if chatroom_id in CHATROOM_CONTROLER.chatroom_pool:
                chatroom = CHATROOM_CONTROLER.chatroom_pool[chatroom_id]
                if chatroom['room_type'] == CHATROOM_CONTROLER.ChatroomType.GroupChat.value \
                        or uid in chatroom['members_id']:
                    ret.append({
                        'chatroom_id': chatroom_id,
                        'title': chatroom['title'],
                        'room_type': chatroom['room_type'],
                    })
                    self.write(dict(status='ok', chatrooms=ret))
                else:
                    self.write(dict(status='fail', error='此聊天室不存在'))
            else:
                self.write(dict(status='fail', error='此聊天室不存在'))
        else:
            # 没有指定具体的聊天室id，返回当前用户的聊天室列表
            current_user = self.db.query(User).filter(User.uid == uid).first()
            chatrooms = list(current_user.chatrooms)

            for chatroom in chatrooms:
                members = []
                for member in chatroom.users:
                    if member.uid != current_user.uid:
                        members.append([member.uid, member.nickname])
                ret.append(
                    {
                        'rid': chatroom.rid,
                        'title': chatroom.title,
                        'room_type': chatroom.room_type,
                        'members': members,
                    }
                )
            self.write(dict(status='ok', chatrooms=ret))

    @check_login_ajax
    def post(self, *args, **kwargs):
        """
        创建chatroom
        :param args:
        :param kwargs:
        :return:
        """
        members_id_str = self.get_argument('members_id')  # member为id，是除自己以外的成员，应该为自己的好友
        members_id = json.loads(members_id_str)
        members_id = list(map(int, members_id))
        assert isinstance(members_id, list)  # 上传的members_id必须是列表类型

        chatroom_type = self.get_argument('chatroom_type', ChatroomsControler.ChatroomType.TempChat.value)  # 要创建的聊天室类型
        chatroom_type = int(chatroom_type)

        members_id = set(members_id)
        members = self.db.query(User.uid, User.nickname).filter(User.uid.in_(members_id)).all()

        if chatroom_type == ChatroomsControler.ChatroomType.TempChat.value:
            title = '临时会话'
        elif chatroom_type == ChatroomsControler.ChatroomType.FriendChat.value:
            title = '好友聊天'
        elif chatroom_type == ChatroomsControler.ChatroomType.GroupChat.value:
            title = self.get_argument('title')  # 群组聊天必须由用户提供标题
        else:
            title = "没有名字的会话"

        # 创建聊天
        chatroom_id = CHATROOM_CONTROLER.create_chatroom(self.session['uid'], title, list(members_id), chatroom_type)

        self.write(dict(
            status='ok',
            chatroom={
                'rid': chatroom_id,
                'title': title,
                'members': members,
            }
        ))


class MessageHandler(BaseHandler):
    @check_login_ajax
    def post(self, *args, **kwargs):
        """
        用户提交消息
        :param args:
        :param kwargs:
        :return:
        """
        current_user = self.db.query(User).filter(User.uid == self.session['uid']).first()
        rid = self.get_argument('rid', None)
        content = self.get_argument('content', None)
        # chatroom = self.db.query(Chatroom).filter(Chatroom.rid == rid).first()
        msg_type = 'TextType'

        # 检查当前用户是否在指定的会话中
        count = self.db.query(ChatroomUsers).filter(
            and_(
                ChatroomUsers.rid == rid,
                ChatroomUsers.uid == current_user.uid,
            )
        ).count()
        if count:
            # 如果是聊天室成员则推送消息通知
            msg_id = CHATROOM_CONTROLER.push_msg(int(rid), current_user.uid, current_user.nickname, content, msg_type)
            if msg_id:
                ret = dict(status='ok', cursor=msg_id)
            else:
                ret = dict(status='fail', error='你不能在此聊天室发言')
        else:
            ret = dict(status='fail', error='你还不是聊天室的成员')
        self.write(ret)

    @check_login_ajax
    def get(self, *args, **kwargs):
        current_user_id = self.session['uid']
        cursor = self.get_argument('cursor', None)
        chatroom_id = int(self.get_argument('chatroom_id'))
        if chatroom_id in CHATROOM_CONTROLER.chatroom_pool and \
                        current_user_id in CHATROOM_CONTROLER.chatroom_pool[chatroom_id]['members_id']:
            messages = CHATROOM_CONTROLER.get_msg(chatroom_id, self.session['uid'], cursor)
            self.write(dict(status='ok', messages=messages))
        else:
            self.write(dict(status='fail', error='该聊天室不存在或已经关闭'))


class SyncHandler(BaseHandler):
    @check_login_ajax
    @gen.coroutine
    def get(self, *args, **kwargs):
        current_user_id = self.session['uid']
        if current_user_id in MIB.member_pool:
            self.future = gen.Future()  # 协程future对象
            if len(MIB.member_pool[current_user_id]['mailbox']) > 0:
                self.future.set_result(list(MIB.member_pool[current_user_id]['mailbox']))   # 如果mailbox中有东西，立即取走，需要转换为list，因返回给浏览器的只能是list
            else:
                MIB.member_pool[current_user_id]['future'] = self.future    # mailbox中没有东西的，
            try:
                chatrooms_id = yield gen.with_timeout(
                    timedelta(seconds=config.future_timeout),
                    self.future,
                    quiet_exceptions=gen.TimeoutError
                )
            except gen.TimeoutError as e:
                chatrooms_id = []
            self.write(dict(status='ok', chatrooms_id=list(chatrooms_id)))
        else:
            MIB.register_member(current_user_id)


class ChatroomMemberHandler(BaseHandler):
    @check_login_ajax
    def get(self, *args, **kwargs):
        chatroom_id = int(self.get_argument('chatroom_id'))
        if chatroom_id:
            ret = CHATROOM_CONTROLER.get_members(chatroom_id)
            self.write(dict(status='ok', members=ret))
        else:
            self.write(dict(status='fail', error='请提供chatroom_id'))

    @check_login_ajax
    def post(self, *args, **kwargs):
        """ 加群申请 """
        current_user_id = self.session['uid']
        chatroom_id = int(self.get_argument('chatroom_id'))
        current_user_nickname = self.session['nickname']
        if chatroom_id in CHATROOM_CONTROLER.chatroom_pool and \
                        CHATROOM_CONTROLER.chatroom_pool[chatroom_id]['room_type'] == CHATROOM_CONTROLER.ChatroomType.GroupChat.value:
            CHATROOM_CONTROLER.push_msg(chatroom_id, current_user_id, current_user_nickname, '申请加群', 'ManageType')
            self.write(dict(status='ok'))
        else:
            self.write(dict(status='fail', error='不存在这个群'))

    def delete(self, *args, **kwargs):
        """ 从指定的聊天室移除成员 """
        current_user_id = self.session['uid']
        chatroom_id = int(self.get_argument('chatroom_id'))
        member_id = int(self.get_argument('member_id'))
        success, msg = CHATROOM_CONTROLER.member_leave(chatroom_id, member_id, current_user_id)
        if success:
            self.write(dict(status='ok'))
        else:
            self.write(dict(status='fail', error=msg))

    def put(self, *args, **kwargs):
        """ 对聊天室内的成员进行修改 """
        chatroom_id = int(self.get_argument('chatroom_id'))
        member_id = int(self.get_argument('member_id', 0))
        current_user_id = self.session['uid']
        current_user_nickname = self.session['nickname']
        action = self.get_argument('action')
        success, msg = False, '没有该操作'
        if action == 'upgrade2manager':
            success, msg = CHATROOM_CONTROLER.being_manager(chatroom_id, member_id, current_user_id)
        elif action == 'manager_down':
            success, msg = CHATROOM_CONTROLER.downgrade_manager(chatroom_id, member_id, current_user_id)
        elif action == 'invite':
            new_member_nickname = self.get_argument('new_member_nickname')
            new_member = self.db.query(User).filter(User.nickname == new_member_nickname).first()
            success = CHATROOM_CONTROLER.members_join(chatroom_id,[new_member.uid, ], current_user_id)
            if success:
                CHATROOM_CONTROLER.push_msg(chatroom_id, current_user_id, current_user_nickname, '我邀请了%s加入聊天' % new_member.nickname, 'TextType')
            msg = None if success else '邀请失败'
        if success:
            self.write(dict(status='ok'))
        else:
            self.write(dict(status='fail', error=msg))


class MuteHandler(BaseHandler):
    @check_login_ajax
    def post(self, *args, **kwargs):
        current_user_id = self.session['uid']
        member_id = int(self.get_argument('member_id'))
        chatroom_id = int(self.get_argument('chatroom_id'))
        flag = self.get_argument('flag') == 'true'

        success, msg = CHATROOM_CONTROLER.mute(current_user_id, chatroom_id, member_id, flag)
        if success:
            self.write(dict(status='ok', msg=msg))
        else:
            self.write(dict(status='fail', error=msg))


class TempChatHandler(BaseHandler):
    @check_login_ajax
    def get(self, *args, **kwargs):
        member_id = self.get_argument('member_id', None)
        current_user_id = self.session['uid']
        if member_id:   # 根据双方id来查找存在的临时会话
            member_id = int(member_id)
            if current_user_id == member_id:
                self.write(dict(status='fail', error='不能与自己创建对话'))
                return
            current_user_tempchat = set(self.db.query(models.Chatroom.rid).filter(
                models.ChatroomUsers.uid == current_user_id,
                models.ChatroomUsers.rid == models.Chatroom.rid,
                models.Chatroom.room_type == CHATROOM_CONTROLER.ChatroomType.TempChat.value,
            ).all())

            member_tempchat = set(self.db.query(models.Chatroom.rid).filter(
                models.ChatroomUsers.uid == member_id,
                models.ChatroomUsers.rid == models.Chatroom.rid,
                models.Chatroom.room_type == CHATROOM_CONTROLER.ChatroomType.TempChat.value,
            ).all())

            temp_chatroom = current_user_tempchat.intersection(member_tempchat)

            if temp_chatroom:
                self.write(dict(status='ok', chatroom_id=temp_chatroom.pop()[0]))
            else:
                new_chatroom_id = CHATROOM_CONTROLER.create_chatroom(current_user_id, '临时会话', [member_id,], CHATROOM_CONTROLER.ChatroomType.TempChat.value)
                self.write(dict(status='ok', chatroom_id=new_chatroom_id))


class GroupMemberHandler(BaseHandler):
    @check_login_ajax
    def post(self, *args, **kwargs):
        current_user_id = self.session['uid']
        current_user_nickname = self.session['nickname']
        chatroom_id = int(self.get_argument('chatroom_id'))
        new_member_id = int(self.get_argument('new_member_id'))
        new_member = self.db.query(models.User).filter(models.User.uid == new_member_id).first()
        result = CHATROOM_CONTROLER.members_join(chatroom_id, [new_member_id, ], current_user_id)
        if result:
            # 成功添加，推送消息
            CHATROOM_CONTROLER.push_msg(chatroom_id, current_user_id, current_user_nickname,
                                        "欢迎%s加入" % new_member.nickname, 'TextType')
            self.write(dict(status='ok'))
        else:
            # 添加失败
            self.write(dict(status='fail', error='添加失败，可能该群不存在或你不是管理员'))


class UploadHandler(BaseHandler):
    @check_login_ajax
    def post(self, *args, **kwargs):
        """ 上传文件组 """
        # 检查聊天室是否存在
        chatroom_id = int(self.get_argument('chatroom_id'))
        if chatroom_id not in CHATROOM_CONTROLER.chatroom_pool:
            self.write(dict(status='fail', error='无法访问该聊天室'))
            return
        files = self.request.files['files']

        # 检测上传的文件是否有超过限定大小
        too_large = []
        for file in files:
            fname = file['filename']
            fsize = len(file['body'])
            if fsize > config.upload_file_size_limit:
                too_large.append({
                    'filename': fname,
                    'size': fsize,
                })
        if len(too_large) > 0:
            self.write(dict(status='fail',
                            error='单个文件体积超出限制%d' % config.upload_file_size_limit,
                            too_large_filelist=too_large))
            return

        # 通过了文件体积限制检查
        current_user_id = self.session['uid']
        current_user_nickname = self.session['nickname']

        for file in files:
            fname = file['filename']
            ftype = file['content_type']
            fpath = os.path.join(config.upload_dir, fname)
            with open(fpath, 'wb') as fp:
                fp.write(file['body'])
            furl = config.upload_url + fname
            msg_id = CHATROOM_CONTROLER.push_msg(chatroom_id, current_user_id, current_user_nickname, furl, 'FileType')
        self.write(dict(status='ok'))

