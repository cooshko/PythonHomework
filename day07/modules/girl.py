#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
from day07.modules.person import Person


class Girl(Person):
    def __init__(self, **kwargs):
        super(Girl, self).__init__(**kwargs)
        self.characteristic = kwargs.get('characteristic', '美女')  # 高富帅、屌丝
