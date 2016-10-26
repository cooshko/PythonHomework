#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : student.class.py
from person import Person
from lesson import Lesson
import datetime


class Student(Person):
    def __init__(self, name, gender, age, password):
        self.name = name    # 学生名字
        self.gender = gender    # 性别
        self.age = age    # 年龄
        self.password = password    # 密码
        self.role = 'student'    # 角色，固定的
        self.lessons = []   # 已选课程。
        self.lesson_log = []    # 上课记录
        self.skills = set()    # 学习到的技能（学习内容）
        self.save()

    def pick_lesson(self, lesson: Lesson):
        """
        选课
        :param lesson:
        :return:
        """
        self.lessons.append(lesson)
        self.save()
        return True

    def take_lesson(self, lesson: Lesson):
        """
        上课
        :param lesson:
        :return:
        """
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lesson.lesson_on()
        self.skills.add(lesson.skill)   # 上课后，学生习得技能
        while True:
            print("你觉得老师讲得怎样？不记名的，放心评价：")
            try:
                t_score = input("0:差评  1:中评  2:好评  ").strip()
                t_score = int(t_score)
                if 0 <= t_score <= 2:
                    lesson.rated(int(t_score))
                    break
                else:
                    print("你的输入有误")
            except Exception as e:
                print("你的输入有误")
        self.lesson_log.append([dt, lesson.name, lesson.teacher.name])
        self.save()

    def display_lessons(self):
        """
        展示已选课程和讲师
        :return:
        """
        print("已选课程如下：")
        fmt = r"%10s %10s %10s %10s"
        print(fmt % ("编号", "课程", "课堂时间", "讲师"))
        for lesson in enumerate(self.lessons):
            print(fmt % (lesson[0], lesson[1].name, lesson[1].classtime, lesson[1].teacher.name))
        return True

    def display_lesson_log(self):
        """
        展示上课记录
        :return:
        """
        print("上课记录如下：")
        fmt = r"%20s %20s %20s"
        print(fmt % ("上课时间", "课程", "讲师"))
        for record in self.lesson_log:
            print(fmt % (record[0], record[1], record[2]))
        return True

    def todo(self):
        while True:
            print('=' * 40)
            commandlist = ['上课', '选课', '查看已选课', '上课记录', '修改密码', '退出']
            for item in enumerate(commandlist):
                print(item[0], item[1])
            choice = input('\n请选择：').strip()
            if choice == '0':
                self.display_lessons()
                tl_num = int(input("\n请输入课堂编号：").strip())
                self.take_lesson(self.lessons[tl_num])
            elif choice == '1':
                print("所有课程如下：")
                all_lessons = Lesson.load_all_lesson()
                for lesson in enumerate(all_lessons):
                    print(lesson[0], lesson[1].name, lesson[1].classtime, lesson[1].teacher.name)
                pl_num = int(input("\n输入选课编号：").strip())
                self.pick_lesson(all_lessons[pl_num])
                print("你已加入 ", all_lessons[pl_num].name)
            elif choice == '2':
                self.display_lessons()
            elif choice == '3':
                self.display_lesson_log()
            elif choice == '4':
                password = input("请输入新密码：").strip()
                if password:
                    self.change_password(password)
                    print("修改密码成功")
                else:
                    print("密码不能为空")
            elif choice == '5':
                break

if __name__ == '__main__':
    stu = Student('coosh', 'male', '25', '123')
    lessons = Lesson.load_all_lesson()
    fmt = r"%10s %10s %10s"
    print(fmt % ("编号", "课程", "讲师"))
    for lesson in enumerate(lessons):
        print(fmt % (lesson[0], lesson[1].name, lesson[1].teacher.name))
    choice = input("输入选修课程的编号：").strip()
    if choice:
        stu.pick_lesson(lessons[int(choice)])
        print("欢迎加入 ", lessons[int(choice)].name)

    print("你所有的课程如下")
    fmt = r"%10s %10s %10s %10s"
    print(fmt % ("编号", "课程", "上课时间", "讲师"))
    for lesson in enumerate(stu.lessons):
        print(fmt % (lesson[0], lesson[1].name, lesson[1].classtime, lesson[1].teacher.name))
    choice = input("输入上哪堂课：").strip()
    if choice:
        stu.take_lesson(stu.lessons[int(choice)])