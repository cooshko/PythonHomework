#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : dump_data.py
import pickle


ds = {
    '广州市':
        {
            '海珠区': {
                '东晓路': {
                    '76中',
                    '广医一院'
                },
                '滨江路': {
                    '帝景苑'
                },
                '燕子岗': {
                    '燕子岗体育场',
                    '万豪酒店'
                }
            },
            '越秀区': {
                '北京路': {
                    '广百百货',
                    '新大新百货'
                },
                '站前路': {
                    '政府机关',
                },
                '东风路': {
                    '正骨医院',
                    '纪念堂',
                    '广东省政府'
                }
            },
        },
    '顺德市':
        {
            '禅城区': {
                '升平路',
                '四海路',
                '锦龙路'
            }
        },
}

if __name__ == '__main__':
    with open('data.pickle', 'wb') as f:
        f.write(pickle.dumps(ds))
