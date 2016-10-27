#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

from boy import Boy
from girl import Girl
import time


def start():
    john = Boy(**dict(name='John', age=20, race='yellow', country='China', skills=['IT', ],
                      salary=0, saving=6666.6, house=0, car=0, gfs=False))
    peter = Boy(**dict(name='Peter', age=25, race='yellow', country='China', skills=['IT', ],
                       salary=50000, saving=666666.6, house=1, car=1, gfs=True, student=False))
    liz = Girl(**dict(name='Liz', age=20, race='yellow', country='China', skills=['跳舞', ],
                      salary=0, saving=6666.6, house=0, car=0))
    all_person = [john, peter, liz]

    year = 0
    story_end = False
    while year < 20:
        year += 1
        print(("第%d年" % year).center(50, '='))
        if year == 1:
            print("大学了".center(50, '*'))
            john.meet(liz)
            john.counting()  # John示爱

        elif year == 5:
            print("毕业了".center(50, '*'))
            john.student = False
            liz.student = False
            john.salary = 5000
            liz.salary = 5000
            peter.meet(liz)
        elif year == 6:
            peter.counting()
            print("Peter 加倍努力工作")
            john.work_hard = 40
        elif year == 7:
            peter.dump_lover()
        elif john.gfs:
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

if __name__ == '__main__':
    start()
