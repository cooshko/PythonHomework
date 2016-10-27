#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
from person import Person


class Boy(Person):
    def __init__(self, **kwargs):
        super(Boy, self).__init__(**kwargs)
        self.gfs = kwargs.get('gfs', False)  # 高富帅，布尔值

    def translate_to_gfs(self):
        if self.saving > 10**6 and not self.gfs:
            print(self.name, "成为了高富帅")
            self.gfs = True
            return True