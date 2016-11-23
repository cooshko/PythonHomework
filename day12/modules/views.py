#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : views.py
import sys
from day12.modules.tables import *


class Views(object):
    @staticmethod
    def create_user_groups(filepath):
        with open(filepath) as fh:
            for line in fh:
                if line.strip():
                    session.add(
                        UserGroup(name=line.strip())
                    )
        session.commit()


if __name__ == '__main__':
    filepath = r"../samples/new_user_groups.txt"
    Views.create_user_groups(filepath)