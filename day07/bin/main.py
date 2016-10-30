#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
import os, sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)
from day07.modules.story import Story

story = Story()
# 参数detail_output = True的话，会输出工作和收入的详细信息
story.start(detail_output=False)
