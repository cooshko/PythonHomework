#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : login-emu.py

import getpass

username = 'coosh'
passwd = '123456'
max_fail_times = 3

fail_time = 0
print(r'Please input username and password')
while True:
    username_input = input('Username: ')
    passwd_input = getpass.getpass(prompt='Password: ')
    if username == username_input and passwd == passwd_input:
        print('Welcome back', username)
        break
    else:
        fail_time += 1
        if fail_time == max_fail_times:
            print('Please try again later.')
            break
        else:
            print('Authentication fail, you have %d chances left.' %
                  (max_fail_times - fail_time))
