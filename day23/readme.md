学员CRM管理系统开发
测试帐号alex，密码123456
网址：http://127.0.0.1:8000/

1. 实现记录学员信息
- 旧版已实现

2. 实现学员学习情况统计
- 旧版已实现，在“学员信息”中

3. 实现学员成绩统计分析
- 旧版已实现，在“学员信息”中

4. 实现班级成绩统计
- 在“班级信息”-> "平均成绩"

5. 不同校区之间信息不共享
- 旧版已实现




旧版readme
学员管理
>* 1.分讲师\学员\课程顾问角色,
>* 7.学校可以有分校区,默认每个校区的员工只能查看和管理自己校区的学员
>* 4.一个学员要有状态转化的过程 ,比如未报名前,报名后,毕业老学员
>* 3.每个班级至少包含一个或多个讲师
>* 2.学员可以属于多个班级,学员成绩按课程分别统计
>* 6.每个学员的所有上课出勤情况\学习成绩都要保存
>* 8.客户咨询要区分来源"
>* 5.客户要有咨询纪录, 后续的定期跟踪纪录也要保存

请注意，本系统有些地方会用到弹出窗口，请确保浏览器不要拦截
网址：http://127.0.0.1:8000/webapp/ （如果你是本机访问的话）
本系统分四个角色，管理员、讲师、学员、课程顾问
其中学员暂不支持登录操作

管理员：主要负责编辑员工（讲师、课程顾问）、课程等。利用django自带的管理站点，他其实就是一个超级用户。
已有帐号：coosh 密码Pass1234

讲师：已有测试帐号alex，密码123456，请于系统网址进行登录。可以对自己主讲的课程发起签到（“发起签到”模块），可以记录学生的成绩（“学员成绩”模块），也可以查看讲师所属校区里的所有学生的成绩和出勤率（“学员信息模块”）。
 
课程顾问：已有测试帐号dan，密码123456，请于系统网址进行登录。“客户咨询”模块，可以让顾问与客户实时聊天，匿名客户访问公开的链接http://127.0.0.1:8000/webapp/consult/ 即可聊天，顾问能实时看到咨询数目，并由系统分配咨询任务。
也可以查看历史聊天。并可记录客户的信息以便进一步跟进 >>“客户跟踪”模块，
就是实现这样的一个功能，顾问既可以在此模块中管理来自咨询的客户，也可以手工添加自己招揽的客户，并对这两类客户安排试听课程。
