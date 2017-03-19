#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
from modules.handlers import *

handlers = [
    (r'/', IndexHandler),
    (r'/login', LoginHandler),
    (r'/register', RegisterHandler),
    (r'/panel', PanelHandler),
    (r'/user', UserHandler),
    (r'/friend', FriendHandler),
    (r'/logout', LogoutHandler),
    (r'/chatroom', ChatroomHandler),
    (r'/message', MessageHandler),
    (r'/sync', SyncHandler),
    (r'/chatroom_member', ChatroomMemberHandler),
    (r'/mute', MuteHandler),
    (r'/temp_chat', TempChatHandler),
    (r'/group_member', GroupMemberHandler),
    (r'/upload', UploadHandler),
]