#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh


class Person:
    detail_output = False
    @staticmethod
    def paint_msg(msg: str):
        return '\033[31;1m' + msg + '\033[0m'

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.age = kwargs.get('age')
        self.job = kwargs.get('job')
        self.income = kwargs.get('income', 3000)    # 月薪
        self.work_hard = kwargs.get('work_hard', 1)  # 工作努力指数，默认为1
        self.race = kwargs.get('race')
        self.country = kwargs.get('country')
        self.skills = kwargs.get('skills')
        self.saving = kwargs.get('saving')
        self.house = kwargs.get('house')
        self.car = kwargs.get('car')
        self.carry_a_torch = kwargs.get('carry_a_torch')    # 单恋
        self.lover = kwargs.get('lover')
        self.student = kwargs.get('student', True)

    def do_the_samething(self):
        self.age += 1
        self.work()

    def work(self):
        """
        工作赚钱，收入跟工作努力程度挂钩
        :return: 工作所得
        """

        if self.student:
            if Person.detail_output:
                msg = "%s 在校读书" % self.name
                print(msg)
        else:
            income = float(self.income * self.work_hard)
            if income > 0:
                if Person.detail_output:
                    print("%s 工作" % self.name)
                self.gain(income)

    def gain(self, money=1.0):
        """
        收入
        :param money:
        :return:
        """
        if Person.detail_output:
            print("%s 得到收入 %.2f" % (self.name, money))
        self.saving += money

    def dump_lover(self):
        msg = "%s 甩掉了 %s" % (self.name, self.lover.name)
        print(Person.paint_msg(msg))
        self.lover.got_dump()
        self.lover = None

    def got_dump(self):
        msg = self.name + " 很伤心，5555"
        print(Person.paint_msg(msg))
        self.lover = None

    def carry_torch_for(self, someone):
        print("%s 对 %s 有好感" % (self, someone))
        self.carry_a_torch = someone

    def counting(self):  # 求爱
        msg = "%s 求爱 %s" % (self, self.carry_a_torch)
        print(Person.paint_msg(msg))
        if self.carry_a_torch.accept_counting(self):
            # 求爱成功
            msg = str(self) + " 求爱成功"
            print(Person.paint_msg(msg))
            self.lover = self.carry_a_torch
            self.carry_a_torch = None
        else:
            msg = str(self) + " 说：我会继续努力的！"
            print(msg)

    def accept_counting(self, someone):
        """
        接受求爱？如果接受且目前有情人，会先抛弃现有情人
        :param someone:
        :return: 接受返回True，否则False
        """
        if self.carry_a_torch == someone:
            msg = str(self) + "说：我愿意"
            print(Person.paint_msg(msg))
            if self.lover:
                self.dump_lover()
            self.lover = someone
            self.carry_a_torch = None
            return True
        else:
            msg = self + "说：很抱歉。。。"
            print(Person.paint_msg(msg))
            return False

    def meet(self, someone):
        # 相遇并互相有好感
        msg = "%s 遇到了 %s" % (self, someone)
        print(Person.paint_msg(msg))
        self.carry_torch_for(someone)
        someone.carry_torch_for(self)

    def __str__(self):
        ret = '{name}({characteristic})'.format(name=self.name, characteristic=self.characteristic)
        return ret

if __name__ == '__main__':
    pass
