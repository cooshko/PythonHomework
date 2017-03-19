#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : common.py
import hashlib, json, redis, uuid, enum
from datetime import datetime, timedelta
from conf.config import redis_session_parameter, redis_chatroom_prefix
from modules import models
from sqlalchemy import and_


def md5(o):
    if isinstance(o, str):
        b = bytes(o, encoding="utf8")
    elif isinstance(o, bytes):
        b = o
    else:
        raise TypeError("应为字符串或bytes类型")
    m = hashlib.md5()
    m.update(b)
    ret = m.hexdigest()
    return ret


class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            # o = o + timedelta(hours=8)
            return o.strftime('%Y-%m-%d %H:%M:%S')
        super(MyJSONEncoder, self).default(o)


# 该类用于全局，保存所有聊天室人员数据，并调度redis
class ChatroomsControler(object):
    Msg_Type = {
        'TextType': 1,
        'FileType': 2,
        'ManageType': 3,
    }

    @enum.unique
    class ChatroomType(enum.Enum):
        FriendChat = 1   # 好友会话
        GroupChat = 2   # 聊天室（多人）会话
        TempChat = 3    # 临时会话

    def __init__(self):
        """
        初始化加载
        """
        try:
            pool = redis.ConnectionPool(host=redis_session_parameter['host'],
                                        port=redis_session_parameter['port'],
                                        password=redis_session_parameter['auth_key'])
            self.redis_server = redis.Redis(connection_pool=pool)
            self.redis_working = True
        except:
            self.redis_working = False

        DBSession = models.sessionmaker(bind=models.engine)
        self.db = DBSession()

        # 读取全部聊天室的数据库数据（聊天记录是存放于redis里）
        all_chatrooms = self.db.query(
            models.Chatroom.rid,
            models.Chatroom.title,
            models.Chatroom.owner,
            models.User.nickname,
            models.Chatroom.room_type,
        ).filter(
            models.Chatroom.owner == models.User.uid
        ).all()

        # 初始化聊天室对象池
        self.chatroom_pool = {}
        for chatroom in all_chatrooms:
            all_members = self.db.query(models.ChatroomUsers.uid, models.ChatroomUsers.speakable).filter(models.ChatroomUsers.rid == chatroom[0]).all()
            all_managers = self.db.query(models.ChatroomManagers.uid).filter(models.ChatroomManagers.rid == chatroom[0]).all()
            mute_members = set(x[0] for x in all_members if not x[1])
            members_id = set([x[0] for x in all_members])
            managers_id = set([x[0] for x in all_managers])
            rid = chatroom[0]
            redis_chatroom_name = self.get_redis_keyname(rid)

            self.chatroom_pool[rid] = {
                'title': chatroom[1],
                'room_type': chatroom[4],
                'owner_id': chatroom[2],
                'owner_nickname': chatroom[3],
                'messages': [],
                'members_id': members_id,
                'managers_id': managers_id,
                'redis_chatroom_name': redis_chatroom_name,
                'mute': mute_members,
            }

            # 读取redis中的历史消息
            if self.redis_working:
                chatroom_messages_b = self.redis_server.lrange(redis_chatroom_name, 0, -1)
                for line in chatroom_messages_b:
                    s = str(line, encoding='utf8')
                    obj = json.loads(s)
                    self.chatroom_pool[rid]['messages'].append(obj)

    def push_msg(self, chatroom_id, member_id, member_nickname, msg, msg_type):
        """
        接收消息，保存到内存，并推送到redis
        :param member_nickname:
        :param chatroom_id:
        :param member_id:
        :param msg:
        :param msg_type:
        :return:
        """
        if chatroom_id in self.chatroom_pool and msg_type in ChatroomsControler.Msg_Type:
            if member_id in self.chatroom_pool[chatroom_id]['mute']:
                return False
            message_id = str(uuid.uuid4())
            new_msg = {
                'message_id': message_id,
                'uid': member_id,
                'nickname': member_nickname,
                'type': ChatroomsControler.Msg_Type[msg_type],
                'content': msg,
            }
            self.chatroom_pool[chatroom_id]['messages'].append(new_msg)

            if self.redis_working:
                self.redis_server.rpush(self.get_redis_keyname(chatroom_id), json.dumps(new_msg))

            # 通知各成员
            # 决定目标受众
            if msg_type == ChatroomsControler.Msg_Type['ManageType']:
                target_person = self.chatroom_pool[chatroom_id]['mangers_id']
            else:
                target_person = self.chatroom_pool[chatroom_id]['members_id']
            for tid in target_person:
                if tid in MIB.member_pool:
                    if MIB.member_pool[tid]['future']:
                        MIB.member_pool[tid]['future'].set_result([chatroom_id, ])  # 如果存在future，则set_result
                    else:
                        MIB.member_pool[tid]['mailbox'].add(chatroom_id)    # 否则，放到mailbox中，等用户自行取走

            # 返回消息ID
            return message_id
        else:
            return False

    def get_msg(self, chatroom_id, member_id, cursor=None):
        """
        获取指定聊天室的聊天记录
        :param cursor:
        :param chatroom_id:
        :param member_id:
        :return:
        """
        if chatroom_id in self.chatroom_pool and member_id in self.chatroom_pool[chatroom_id]['members_id']:
            # 聊天室存在，且给定的成员ID在聊天室内
            isManager = member_id in self.chatroom_pool[chatroom_id]['managers_id']     # 给定用户是否管理员
            all_messages = []   # 用于存放未过滤的所有消息
            ret = []    # 用于存放最终返回的消息列表
            if cursor:
                # 如果有给定游标
                found = False
                index = 1
                for msg in self.chatroom_pool[chatroom_id]['messages']:
                    if msg['message_id'] == cursor:
                        found = True
                        break
                    index += 1
                if found and index < len(self.chatroom_pool[chatroom_id]['messages']):
                    all_messages = self.chatroom_pool[chatroom_id]['messages'][index:]
            else:
                # 如果没有给定游标，则全部消息
                all_messages = self.chatroom_pool[chatroom_id]['messages']

            # 检查是否管理员，如果不是管理员，将不能接收管理类的消息
            for msg in all_messages:
                if msg['type'] == ChatroomsControler.Msg_Type['ManageType'] and not isManager:
                    continue
                else:
                    ret.append(msg)
            return ret

    def get_redis_keyname(self, chatroom_id):
        """ 获取聊天室对应的redis键名 """
        ret = '%s.%s' % (redis_chatroom_prefix, str(chatroom_id))
        return ret

    def members_join(self, chatroom_id, members_id: list, manager_id: int):
        """
        批量会员加入某聊天室
        :param chatroom_id:
        :param members_id:
        :return:
        """
        if chatroom_id in self.chatroom_pool:   # 判断聊天室是否存在
            # 如果提交的管理员ID，不属于指定群，则不允许添加
            members_id = set(members_id)
            if manager_id not in self.chatroom_pool[chatroom_id]['managers_id']:
                return False
            for uid in members_id:
                if uid not in self.chatroom_pool[chatroom_id]['members_id']:
                    # 检查用户是否在该聊天室里，如果不是，则加入
                    count = self.db.query(models.ChatroomUsers).filter(
                        and_(
                            models.ChatroomUsers.uid == uid,
                            models.ChatroomUsers.rid == chatroom_id,
                        )
                    ).count()
                    if count == 0:
                        self.db.add(
                            models.ChatroomUsers(uid=uid, rid=chatroom_id)
                        )
                        self.db.commit()

                    # 加入到服务器的聊天室成员池里
                        self.chatroom_pool[chatroom_id]['members_id'] = self.chatroom_pool[chatroom_id]['members_id'].union(members_id)
            return True
        else:
            return False

    def member_leave(self, chatroom_id, member_id, from_id):
        """
        成员离开指定聊天室
        可以是被踢，也可以是主动离开
        :param from_id:
        :param chatroom_id:
        :param member_id:
        :return:
        """
        if chatroom_id in self.chatroom_pool:  # 判断聊天室是否存在
            chatroom = self.chatroom_pool[chatroom_id]
            if from_id != member_id:
                if from_id not in chatroom['managers_id']:
                    return False, '普通用户不能移除别的成员'
                elif member_id in chatroom['managers_id'] and from_id != chatroom['owner_id']:
                    return False, '只有群主才能移除别的管理员'

            # 判断，成员是否群主本人，
            # 如果是，则视为解散群；
            # 如不是，则只踢走指定用户
            # 踢走成员后，如果members_id只剩下两个，也应该解散群
            if member_id == chatroom['owner_id']:
                self.shutdown_chatroom(chatroom_id)
                return True, None
            else:
                if len(chatroom['members_id']) <= 3:    # 如果只剩下3个人或一下，再走一个的话，就应解散
                    self.shutdown_chatroom(chatroom_id)
                    return True, None
                else:
                    # 正常移除指定成员
                    # 删除数据库中的关联
                    self.db.query(models.ChatroomUsers).filter(
                        and_(
                            models.ChatroomUsers.uid == member_id,
                            models.ChatroomUsers.rid == chatroom_id,
                        )
                    ).delete()
                    self.db.commit()

                    # 清理聊天室成员池里的成员
                    chatroom['members_id'].remove(member_id)
                    if member_id in chatroom['managers_id']:
                        chatroom['managers_id'].remove(member_id)

                    return True, None

    def create_chatroom(self, owner_id: int, title: str, members_id: list,  chatroom_type: int):
        """
        创建聊天室
        :param owner_id:
        :param title:
        :param members_id:
        :param chatroom_type:
        :return: 应返回chatroom_id
        """

        # 对数据库的处理
        chatroom_obj = models.Chatroom()
        chatroom_obj.title = title
        chatroom_obj.owner = owner_id
        chatroom_obj.room_type = chatroom_type
        self.db.add(chatroom_obj)
        self.db.commit()

        owner = self.db.query(models.User).filter(models.User.uid == owner_id).first()
        members = self.db.query(models.User).filter(models.User.uid.in_(members_id)).all()

        chatroom_obj.users.append(owner)
        chatroom_obj.users.extend(members)
        chatroom_obj.managers.append(owner)
        self.db.commit()

        # 对聊天室内存池的处理
        self.chatroom_pool[chatroom_obj.rid] = {
            'title': title,
            'room_type': chatroom_obj.room_type,
            'owner_id': owner_id,
            'owner_nickname': owner.nickname,
            'messages': [],
            'members_id': members_id + [owner_id, ],
            'managers_id': [owner_id, ],
            'redis_chatroom_name': self.get_redis_keyname(chatroom_obj.rid),
            'mute': set(),
        }

        return chatroom_obj.rid

    def shutdown_chatroom(self, chatroom_id):
        """
        关闭某聊天室，清理聊天室池
        :param chatroom_id:
        :return:
        """
        # 移除数据库的关联
        self.db.query(models.ChatroomUsers).filter(
            models.ChatroomUsers.rid == chatroom_id
        ).delete()
        self.db.query(models.Chatroom).filter(
            models.Chatroom.rid == chatroom_id
        ).delete()
        self.db.commit()

        # 移除CHATROOM内存池数据
        if chatroom_id in self.chatroom_pool:
            del self.chatroom_pool[chatroom_id]

        # 移除redis聊天记录
        if self.redis_working:
            self.redis_server.delete(self.get_redis_keyname(chatroom_id))

    def get_members(self, chatroom_id):
        """
        读取指定聊天室的成员列表
        :param chatroom_id:
        :return:
        """
        if chatroom_id not in self.chatroom_pool:
            return []
        chatroom = self.chatroom_pool[chatroom_id]
        ret = []
        all_members = self.db.query(models.User.uid, models.User.nickname, models.ChatroomUsers.speakable).filter(
            models.ChatroomUsers.rid == chatroom_id,
            models.ChatroomUsers.uid == models.User.uid,
            models.User.uid.in_(self.chatroom_pool[chatroom_id]['members_id']),
        ).all()
        for member in all_members:
            uid = member[0]
            nickname = member[1]
            speakable = member[2]
            isOwner = uid == chatroom['owner_id']
            isManager = uid in chatroom['managers_id']
            ret.append({
                'uid': uid,
                'nickname': nickname,
                'isOwner': isOwner,
                'isManager': isManager,
                'speakable': speakable,
            })
        return ret

    def mute(self, from_id, chatroom_id, member_id, flag):
        """
        指定聊天室内禁言指定用户
        :param from_id: 发起禁言请求的用户id
        :param flag: bool，True：禁言    False：解禁
        :param chatroom_id: 聊天室id
        :param member_id: 被禁言的用户id
        :return:
        """
        if chatroom_id not in self.chatroom_pool:
            return False, '该聊天室不存在'

        chatroom = CHATROOM_CONTROLER.chatroom_pool[chatroom_id]

        if from_id == member_id:
            return False, '不能禁言或解禁自己'

        # 检查from_id是否指定聊天室的管理员
        from_manager = from_id in chatroom['managers_id']
        if not from_manager:
            return False, '普通成员不允许该操作，请联系管理员或群主'

        # 不能禁言群主
        member_is_owner = member_id == chatroom['owner_id']
        if member_is_owner:
            return False, '不能禁言群主'

        # 检查被禁言的用户是否管理员
        member_is_manager = member_id in chatroom['managers_id']
        if member_is_manager and from_id != chatroom['owner_id']:
            return False, '只有群主可以禁言或解禁管理员'

        # 通过上两个检查后
        record = self.db.query(models.ChatroomUsers).filter(
            models.ChatroomUsers.uid == member_id,
            models.ChatroomUsers.rid == chatroom_id,
        ).first()
        if flag:
            # flag为True，禁言
            chatroom['mute'].add(member_id)
            record.speakable = False
            self.db.commit()
            return True, '已禁言该用户'
        else:
            # flag为True，解禁
            chatroom['mute'].remove(member_id)
            record.speakable = True
            self.db.commit()
            return True, '已解禁该用户'

    def notify_members(self, chatroom_id: int, msg_type):
        if chatroom_id in self.chatroom_pool:   # 如果该聊天室存在于池中
            if msg_type == self.Msg_Type['ManageType']:
                # 如果该消息是管理类的消息，则目标人群只限于管理员
                target_person = self.chatroom_pool[chatroom_id]['managers_id']
            else:
                # 否则目标人群是该聊天室的所有成员
                target_person = self.chatroom_pool[chatroom_id]['members_id']

            for tid in target_person:    # 循环目标人群
                if tid in MIB.member_pool:  # 目标人群存在成员内存池当中
                    if MIB.member_pool[tid]['future']:  # 如果存在future，则立即set_result
                        MIB.member_pool[tid]['future'].set_result(set(chatroom_id))
                    else:   # 不存在future，则记录到用户的mailbox中
                        MIB.member_pool[tid]['mailbox'].add(chatroom_id)

    def being_manager(self, chatroom_id, member_id, from_id):
        """  指定用户为管理员 """
        if chatroom_id in self.chatroom_pool:
            chatroom = self.chatroom_pool[chatroom_id]
            if from_id == chatroom['owner_id']:
                # 数据库的操作
                new_manager = models.ChatroomManagers()
                new_manager.rid = chatroom_id
                new_manager.uid = member_id
                self.db.add(new_manager)
                self.db.commit()

                # 聊天室内存池的操作
                chatroom['managers_id'].add(member_id)

                return True, None
            else:
                return False, '该操作只能由群主执行'
        else:
            return False, '没有此聊天室'

    def downgrade_manager(self, chatroom_id, member_id, from_id):
        """ 将管理员降级 """
        if chatroom_id in self.chatroom_pool:
            chatroom = self.chatroom_pool[chatroom_id]
            if from_id == chatroom['owner_id']:
                # 数据库的操作
                self.db.query(models.ChatroomManagers).filter(
                    and_(
                        models.ChatroomManagers.rid == chatroom_id,
                        models.ChatroomManagers.uid == member_id,
                    )
                ).delete()

                # 聊天室内存池的操作
                if member_id in chatroom['managers_id']:
                    chatroom['managers_id'].remove(member_id)

                return True, None
            else:
                return False, '该操作只能由群主执行'
        else:
            return False, '没有此聊天室'

CHATROOM_CONTROLER = ChatroomsControler()


class MemberInfoBox(object):
    def __init__(self):
        self.member_pool = {}

    def register_member(self, uid):
        # 成员池里创建给定uid的字典
        if uid not in self.member_pool:
            self.member_pool[uid] = {
                'mailbox': set(),   # 当用户的future不能成功返回时，把有新消息的聊天室ID存到mailbox
                'future': None, # 用于存放用户的future
            }

    def unregister_member(self, uid):
        # 删除成员池里的给定uid
        if uid in self.member_pool:
            del self.member_pool[uid]

MIB = MemberInfoBox()
