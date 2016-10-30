#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
from day07.modules.person import Person


class Boy(Person):
    def __init__(self, **kwargs):
        super(Boy, self).__init__(**kwargs)
        self.gender = '男'
        self.characteristic = kwargs.get('characteristic', '屌丝')  # 高富帅、屌丝

    def translate_to_gfs(self):
        if self.saving > 10**6 and self.characteristic != '高富帅':
            msg = "{name} 成为了高富帅，资产达到了{saving:,.2f}".format(name=self, saving=self.saving)
            print(Boy.paint_msg(msg))
            self.characteristic = '高富帅'
            return True