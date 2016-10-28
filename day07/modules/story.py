#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

from day07.modules.boy import Boy
from day07.modules.girl import Girl
from day07.modules.person import Person
import time


class Story:
    def start(self, detail_output=False):
        Person.detail_output = detail_output
        john = Boy(**dict(name='John', age=20, race='yellow', country='China', skills=['IT', ],
                          income=0, saving=6666.6, house=0, car=0))
        peter = Boy(**dict(name='Peter', age=25, race='yellow', country='China', skills=['IT', ],
                           income=50000, saving=666666.6, house=1, car=1, characteristic='高富帅', student=False))
        liz = Girl(**dict(name='Liz', age=20, race='yellow', country='China', skills=['跳舞', ],
                          income=0, saving=6666.6, house=0, car=0))
        all_person = [john, peter, liz]

        year = 0
        story_end = False
        while year < 20:
            year += 1
            print(("第%d年" % year).center(50, '='))
            if year == 1:
                print("大学".center(30, '*'))
                john.meet(liz)
                john.counting()  # John示爱

            elif year == 5:
                print("毕业".center(30, '*'))
                john.student = False
                liz.student = False
                john.income = 50000
                liz.income = 50000
                peter.meet(liz)
            elif year == 6:
                peter.counting()
                john.work_hard = 4
                print("John 加倍努力工作，年收入达到{income:,.2f}".format(income=john.income*john.work_hard))

            elif year == 7:
                peter.dump_lover()
            elif john.characteristic == '高富帅':
                liz.meet(john)
                liz.counting()
                story_end = True

            for p in all_person:
                p.do_the_samething()
                if isinstance(p, Boy):
                    p.translate_to_gfs()
            if story_end:
                break
            time.sleep(1)


