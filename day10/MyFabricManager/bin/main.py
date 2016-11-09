#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

import os, sys, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT)
from day10.MyFabricManager.modules.mfm import Mfm

if __name__ == '__main__':
        mfm = Mfm(isdebug=True)
        mfm.router()