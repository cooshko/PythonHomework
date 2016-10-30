#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

from day07.modules.boy import Boy
from day07.modules.girl import Girl
from day07.modules.person import Person
import time


class Story:
    def start(self, detail_output=False):
        # 故事开始
        Person.detail_output = detail_output    # 控制是否输出详细的收入信息
        john = Boy(**dict(name='John', age=20, race='yellow', country='China', skills=['IT', ],
                          income=0, saving=6666.6, house=0, car=0))
        peter = Boy(**dict(name='Peter', age=25, race='yellow', country='China', skills=['IT', ],
                           income=50000, saving=666666.6, house=1, car=1, characteristic='高富帅', student=False))
        liz = Girl(**dict(name='Liz', age=20, race='yellow', country='China', skills=['跳舞', ],
                          income=0, saving=6666.6, house=0, car=0))

        all_person = [john, peter, liz] # 将演员都放到一个池里

        year = 0
        story_end = False   # 故事结束标记
        while not story_end:
            year += 1
            print(("第%d年" % year).center(50, '='))

            if year == 1:
                # 故事的第一年，John与Liz大学相遇
                print("大学".center(30, '*'))
                john.meet(liz)
                john.counting()  # John示爱

            elif year == 4:
                # 故事第四年，John与Liz仍是情侣；
                # 毕业了，两人找到了工作，而Liz遇到了Peter
                print("毕业".center(30, '*'))
                john.student = False
                liz.student = False
                john.income = 50000
                liz.income = 50000
                peter.meet(liz)
            elif year == 5:
                # 故事第五年，Peter向Liz求爱
                if peter.counting():
                    # 如果Peter求爱Liz成功，John尝试挽回Liz
                    john.carry_torch_for(liz)
                    if not john.counting():
                        # 如果John挽回失败，就加倍努力工作，希望成为高富帅
                        john.work_hard = 4
                        print("John 加倍努力工作，年收入达到{income:,.2f}".format(income=john.income*john.work_hard))

            elif year == 7:
                # 故事第七年，Peter甩掉了Liz
                peter.dump_lover()
            elif john.characteristic == '高富帅':
                # 故事第N年（仅当John成为了高富帅），Liz重遇John，并复合，故事结束
                liz.meet(john)
                liz.counting()
                story_end = True

            for p in all_person:
                # 每个角色都必须工作、收入等动作
                p.do_the_samething()
                if isinstance(p, Boy):
                    # 如果是男角色，会尝试改变角色定位到高富帅
                    p.translate_to_gfs()

            # 休眠一秒，当一年过去了
            time.sleep(1)


