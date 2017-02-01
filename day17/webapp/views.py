from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django import views
from django.contrib.auth.views import AuthenticationForm
from django.core.paginator import Paginator, EmptyPage, \
    PageNotAnInteger  # 导入的Paginator是分页器，而EmptyPage和PageNotAnInteger是异常类
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.db.models import functions, DateTimeField
from . import models, forms
from .decorators import *
from datetime import datetime, timedelta
from collections import OrderedDict
import json, random, hashlib


class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            o = o + timedelta(hours=8)
            return o.strftime('%Y-%m-%d %H:%M:%S')
        super(DateTimeJSONEncoder, self).default(o)


# 登录页面
def login(request):
    if request.method == 'POST':
        """用户提交验证数据"""
        loginForm = forms.LoginForm(request.POST)
        if loginForm.is_valid():
            """提交的数据合法"""
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = models.StudentInfo.objects.filter(name=username, password=password, status__name='已报名').first() or \
                   models.StaffInfo.objects.filter(sysname=username, password=password, status__name='在职').first()
            if user:
                """验证通过"""
                user_dict = model_to_dict(user, exclude=['courses', ])  # 针对StudentInfo，需要排除多对多
                request.session['user'] = user_dict
                request.session['user_roles'] = []
                if isinstance(user, models.StaffInfo):
                    request.session['user_type'] = 'staff'
                    request.session['user_roles'] = ['员工', user.roles.name]
                    redirect_url = reverse("webapp:staff")
                else:
                    request.session['user_type'] = 'student'
                    request.session['user_roles'] = ['学员', ]
                    redirect_url = reverse("webapp:student")
                response_str = json.dumps({'status': 'ok', 'url': redirect_url})
                return redirect(reverse("webapp:index"))
            else:
                return HttpResponse(json.dumps({'status': 'fail', 'msg': "验证不通过"}))

    else:
        """用户打开登录界面"""
        loginForm = AuthenticationForm()
    return render(request, "app/login.html", {'loginForm': loginForm})


# 注销
def logout(request):
    request.session.clear()
    return redirect(reverse("webapp:index"))


# 首页，根据用户类型不同重定向到用户首页
@check_login
def index(request):
    """
    首页
    :param request:
    :return:
    """
    user_type = request.session.get("user_type")
    if user_type:
        return redirect(reverse("webapp:" + user_type))


# 学校员工首页
@check_login
@check_roles(["员工", ])
def staff_index(request):
    """学校员工首页"""
    user = request.session.get("user")
    return render(request, "app/base-staff.html", {'roles': request.session.get("user_roles", []),
                                                   'user': user})


# 学员首页
@check_login
@check_roles(["学员", ])
def student_index(request):
    """学生首页"""
    return HttpResponse("这是学生首页")


# 考勤页面
@check_login
@check_roles(["员工", ])
def attendance(request):
    """签到页面"""
    user_dict = request.session.get('user')
    tid = user_dict['id']
    course_id = request.GET.get('course_id')
    current_datetime = datetime.now()
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day
    if request.method == 'GET':
        if course_id:
            # 获取指定课程学员信息
            course = models.Course.objects.get(id=course_id)
            students = models.StudentInfo.objects.filter(courses__id=course_id)
            # 获取当天已签到的记录
            attended_students = models.Attendance.objects.annotate(
                attend_day=functions.Trunc('attend_time',
                                           'day',
                                           output_field=DateTimeField(), )
            ).filter(attend_day=datetime(year, month, day), course_id=course_id).values_list('student_id', flat=True)
            return render(request, "app/attendance-course.html", {'students': students,
                                                                  'course': course,
                                                                  'current_date': current_datetime,
                                                                  'attended_students': attended_students})
        else:
            # 返回当前讲师的课程
            course_list = models.Course.objects.filter(teachers__id=tid)
            return render(request, "app/attendance-courses-list.html", {'courses': course_list})
    elif request.method == 'POST':
        # POST签到数据
        student_id = request.POST.get("student_id")
        action = request.POST.get("action", "attend")
        if student_id:
            if action == "attend":
                # 签到
                models.Attendance.objects.create(student_id=student_id,
                                                 course_id=course_id,
                                                 attend_time=current_datetime)
                return HttpResponse(
                    json.dumps({'status': 'ok', 'attend_time': current_datetime.strftime("%Y-%m-%d %H:%M:%S")}))
            elif action == "cancel":
                a = models.Attendance.objects.filter(student_id=student_id,
                                                     course_id=course_id,
                                                     attend_time=current_datetime)
                # a.delete()
                return HttpResponse(json.dumps({'status': 'ok'}))


# 成绩页面
@check_login
@check_roles(["讲师", ])
def score(request):
    """录入成绩"""
    current_user = request.session["user"]
    course_id = request.GET.get("course_id")
    if request.method == 'GET':
        if course_id:
            # 获取指定课程的学员成绩
            course = models.Course.objects.get(id=course_id)
            students = models.Course.objects.get(id=course_id).studentinfo_set.all()
            # x = students[4].coursescore_set.first()
            return render(request, "app/score-course-students.html", {"course": course,
                                                                      "students": students})
        else:
            # 获取当前讲师的课程列表
            tid = current_user['id']
            course_list = models.StaffInfo.teachers.get(id=tid).course_set.all().order_by('-start_time')
            return render(request, "app/score-course-list.html", {"course_list": course_list})
    elif request.method == 'POST':
        json_str = request.POST.get("json_str")
        queue = json.loads(json_str)
        modified_queue = queue.get("modified_queue")
        new_queue = queue.get("new_queue")
        fail_list = []
        if len(modified_queue) > 0:
            # 修改历史数据
            for item in modified_queue:
                student_id = item.get("student_id")
                score = item.get("score")
                try:
                    score = int(score)
                    if 1 <= score <= 100:
                        models.CourseScore.objects.filter(course_id=course_id, student_id=student_id) \
                            .update(score=score, updated_by_id=current_user['id'])
                    else:
                        raise ValueError
                except:
                    fail_list.append({'student_id': student_id,
                                      'score': score,
                                      'msg': '请提供1至100的数字，并且必须为整数。'})

        if len(new_queue) > 0:
            # 添加新数据
            for item in new_queue:
                student_id = item.get("student_id")
                score = item.get("score")
                models.CourseScore.objects.create(student_id=student_id,
                                                  course_id=course_id,
                                                  score=score,
                                                  updated_by_id=current_user['id'])
        if len(fail_list) > 0:
            return HttpResponse(json.dumps({
                'status': 'fail',
                'msg': fail_list,
            }))
        else:
            return HttpResponse(json.dumps({'status': 'ok', }))


# 员工获取学员列表
@check_login
@check_roles(["员工", ])
def manage_student_list(request):
    current_staff = request.session.get("user")
    area_id = current_staff.get("area")
    student_list = models.StudentInfo.objects.filter(area_id=area_id).all()

    # 分页
    page_num = request.GET.get("page")  # 获取URL中page参数
    paginator = Paginator(student_list, 5)
    try:
        student_page = paginator.page(page_num)  # 分页器根据URL中page参数来返回一个Page对象，这个对象是可迭代的，迭代返回的是一个Model
    except EmptyPage:
        student_page = paginator.page(paginator.num_pages)  # 当分页器抛出异常通常有两种情况，第一种是请求的页数太大，捕获到这种异常后，返回最后一页即可
    except PageNotAnInteger:
        student_page = paginator.page(1)  # 还有一种是page不存在或者类型错误，这时返回第一页内容
    return render(request, "app/manage_student_list.html", {"students": student_page})


# 获取指定学员的指定课程的出勤数据
@check_login
@check_roles(["员工", ])
def get_student_attendance_by_course(request, student_id, course_id):
    # 获取指定课程的上课日列表
    course_days = models.Attendance.objects.annotate(
        attend_day=functions.Trunc('attend_time', 'day', output_field=DateTimeField(), )
    ).filter(course_id=course_id) \
        .values_list('attend_day', flat=True) \
        .distinct() \
        .order_by('attend_day')
    # 利用上课日作为key，预生成一个字典
    attendance_dict = OrderedDict()
    for the_day in course_days:
        attendance_dict[the_day.strftime('%Y-%m-%d')] = False

    # 获取该学员这个课程的出勤具体时间的列表
    student_attend_course_days = models.Attendance.objects.filter(course_id=course_id, student_id=student_id) \
        .values_list('attend_time', flat=True).order_by('-attend_time')
    # 把每一个时间拆分成日期和时间，如果日期存在于上面的生成的字典里，则把时间赋值到字典里
    for the_day in student_attend_course_days:
        d, t = (the_day + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M').split(' ')
        if d in attendance_dict:
            attendance_dict[d] = t

    return HttpResponse(json.dumps(attendance_dict))


# 员工获取学员列表
@check_login
@check_roles(["员工", ])
def manage_student(request, student_id=None):
    student = models.StudentInfo.objects.get(id=student_id)
    if request.method == 'GET':
        all_status = models.StudentStatus.objects.all()
        return render(request, "app/manage-student-detail.html", {'student': student, 'all_status': all_status})
    else:
        # POST
        new_status_id = request.POST.get("new_status_id")
        if new_status_id:
            new_status = models.StudentStatus.objects.get(id=new_status_id)
            if new_status:
                student.status = new_status
                student.save()
                return HttpResponse(json.dumps({"status": "ok"}))
            else:
                return HttpResponse(json.dumps({"status": "fail", "msg": "没有这个状态"}))


# 课程顾问咨询页面
@check_login
@check_roles(["课程顾问", ])
def consult(request):
    """客户咨询"""
    staff_dict = request.session.get("user")
    if request.method == 'GET':
        if request.GET:
            # 有参数
            action = request.GET.get("action")
            if action == "check_consult_num":
                # 如果action是读取待处理咨询的数量
                num = models.SessionTokens.objects.filter(staff=None, active=True).count()
                return HttpResponse(json.dumps({"count": num}))

            elif action == "get_a_job":
                # 分配一个待处理的咨询给当前员工
                st = models.SessionTokens.objects.filter(staff=None, active=True).first()
                st.staff_id = staff_dict['id']
                st.save()
                return HttpResponse(json.dumps({"token": st.token, "source": st.source}))

                # elif action == "open_a_consult":
                #     # 打开一个咨询
                #     token = request.GET.get("token")
                #     if token:
                #         # 如果URL中有token，代表打开一个已存在的咨询会话，但必须是active并且staff_id是当前员工
                #         # st = models.SessionTokens.objects.get(token=token, staff_id=staff_dict['id'], active=True)
                #         # st = get_object_or_404(models.SessionTokens, token=token, staff_id=staff_dict['id'], active=True)
                #         st = get_object_or_404(models.SessionTokens, token=token,  active=True)
                #         if st.source == 'web':
                #             cc = list(models.ClientConsult.objects.filter(session=st).values())
                #             return HttpResponse(json.dumps(cc, cls=DateTimeJSONEncoder))
                #     else:
                #         # 如果URL中没有token，则由系统分配一个咨询会话给客户端
                #         pass

        else:
            # 无参数只返回页面
            return render(request, "app/consult-staff-page.html")


@check_login
@check_roles(["课程顾问", ])
def consult_chat(request):
    token = request.GET.get("token")
    current_staff = request.session.get("user")
    st = get_object_or_404(models.SessionTokens, token=token, staff_id=current_staff['id'])
    if request.method == 'GET':
        ci = models.ClientInfo.objects.filter(token__token=token).first()
        ret = render(request, "app/consult-chat-staff.html", {'st': st, 'ci': ci})
        return ret
    else:
        msg = request.POST.get("msg")
        st = get_object_or_404(models.SessionTokens, token=token, staff_id=current_staff['id'])
        if st.active:
            cc = models.ClientConsult.objects.create(session=st, msg=msg, from_client=False)
            return HttpResponse(json.dumps({'status': 'ok', 'lastMsgID': cc.id}))
        else:
            return HttpResponse(json.dumps({'status': 'fail', 'msg': '该会话已经关闭。'}))


@check_login
@check_roles(["课程顾问", ])
def staff_get_msg(request):
    current_staff = request.session.get("user")
    token = request.GET.get("token")
    lastMsgID = int(request.GET.get("lastMsgID", 0))
    st = get_object_or_404(models.SessionTokens, token=token, staff_id=current_staff['id'])
    msg_list = list(models.ClientConsult.objects.filter(session=st, id__gt=lastMsgID).values())
    return HttpResponse(json.dumps(msg_list, cls=DateTimeJSONEncoder))


# 课程顾问定期跟踪未报名客户
@check_login
@check_roles(["课程顾问", ])
def follow_up(request):
    """定期跟踪未报名客户"""
    if request.method == 'GET':
        # 下面的ci的意思是，找出所有未成为学员的客户资料
        # 要实现该功能，首先要把StudentInfo表中所有的client_id都找出来，且不能为空
        # 排除掉所有成为学员的客户后，再排除不需要再跟进的客户
        ci = models.ClientInfo.objects.exclude(
            id__in=set(models.StudentInfo.objects.filter(
                client_id__isnull=False)
                       .values_list('client_id', flat=True))).filter(dont_follow=False).order_by("-create_at")
        return render(request, "app/followup-page.html", {"ci": ci})
    # return HttpResponse("定期跟踪未报名客户")


# 课程顾问让客户参加试听
@check_login
@check_roles(["课程顾问", ])
def experiencing(request):
    """试听课程"""
    return HttpResponse("客户参与试听")


# 匿名客户咨询
def consult_from_guest(request):
    if request.method == 'GET':
        # 获取咨询页面，每一次获取都视为一个新的会话
        # 每一个会话都有一个token作为凭据和标识
        # 根据客户ip地址、当前服务器时间、一个随机数生成一个MD5值作为token
        remote_ip = ""
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            remote_ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            remote_ip = request.META['REMOTE_ADDR']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        salt = str(random.random())
        m = hashlib.md5()
        m.update((now + remote_ip + salt).encode())
        token = m.hexdigest()

        # 写入SessionTokens表
        staff_dict = request.session.get("user")
        st = models.SessionTokens.objects.create(client_ip=remote_ip, token=token)

        # token附带在cookie中
        ret = render(request, "app/consult-chat.html", )
        ret.set_cookie('token', token)
        return ret
    else:
        token = request.COOKIES.get("token", "")
        msg = request.POST.get("msg")
        st = models.SessionTokens.objects.get(token=token)
        if st and st.active:
            cc = models.ClientConsult.objects.create(session=st, msg=msg, from_client=True)
            return HttpResponse(json.dumps({'status': 'ok', 'lastMsgID': cc.id}))
        else:
            return HttpResponse(json.dumps({'status': 'fail', 'msg': "当前会话已完结或不存在。"}))


# 客人获取新消息
def client_get_msg(request):
    token = request.GET.get("token")
    lastMsgID = int(request.GET.get("lastMsgID", 0))
    st = get_object_or_404(models.SessionTokens, token=token)
    msg_list = list(models.ClientConsult.objects.filter(session=st, id__gt=lastMsgID).values())
    return HttpResponse(json.dumps(msg_list, cls=DateTimeJSONEncoder))


# 获取当前员工处理中的咨询（未关闭，active为True）
@check_login
@check_roles(["课程顾问", ])
def get_handling(request):
    current_staff = request.session.get("user")
    if request.method == 'GET':
        # st = list(models.SessionTokens.objects.filter(staff_id=current_staff['id'], active=True).values('token', 'create_at'))
        # return HttpResponse(json.dumps(st, cls=DateTimeJSONEncoder))
        st = models.SessionTokens.objects \
            .filter(staff_id=current_staff['id']) \
            .values('clientinfo__name', 'token', 'create_at')
        handling_list = list(st.filter(active=True).all())
        finished_list = list(st.filter(active=False).all())
        ret = {
            'handling_list': handling_list,
            'finished_list': finished_list
        }
        return HttpResponse(json.dumps(ret, cls=DateTimeJSONEncoder))


# 员工关闭咨询，AJAX
@check_login
@check_roles(["课程顾问", ])
def close_a_consult(request):
    current_staff = request.session.get("user")
    token = request.GET.get("token")
    if request.method == 'GET':
        st = models.SessionTokens.objects.get(staff_id=current_staff['id'], token=token)
        if st.active:
            st.active = False
            st.save()
            return HttpResponse(json.dumps({'status': 'ok'}))
        else:
            return HttpResponse(json.dumps({'status': 'fail',
                                            'msg': "会话不存在或者已关闭"}))


# 保存咨询客户信息，AJAX
@check_login
@check_roles(["课程顾问", ])
def save_client_info(request):
    current_staff = request.session.get("user")
    if request.method == 'POST':
        # 用户把客户信息post上来
        token = request.POST.get("token")
        client_name = request.POST.get("name")
        client_phone = request.POST.get("phone")
        client_qq = request.POST.get("qq")
        client_email = request.POST.get("email")
        client_remark = request.POST.get("remark")
        st = models.SessionTokens.objects.filter(token=token).first()

        if client_phone or client_qq or client_email:
            # 电话、qq、email必须有其中一个
            ci = models.ClientInfo.objects.filter(token=st).first()
            if ci:
                # 已经存在客户资料，需要在客户跟进中记录一下原值
                old_values = "{}修改了该客户资料，原值如下\n称谓：{}\n电话：{}\nQQ：{}\n邮箱：{}\n备注：{}\n"\
                    .format(current_staff['cname'],
                            ci.name,
                            ci.phone,
                            ci.qq,
                            ci.email,
                            ci.remark)
                models.ClientFollowUp.objects.create(client=ci,
                                                     staff_id=current_staff['id'],
                                                     follow_time=datetime.utcnow(),
                                                     result=old_values)
            else:
                ci = models.ClientInfo()
                # models.ClientInfo.objects.create(name=client_name, qq=client_qq, phone=client_phone,
                #                                  email=client_email, remark=client_remark, token_id=st.id)
                # return HttpResponse(json.dumps({"status": "ok", "msg": "已保存，并可在客户跟进中查看"}))
            ci.name = client_name
            if client_qq:
                ci.qq = client_qq
            ci.phone = client_phone
            ci.email = client_email
            ci.remark = client_remark
            ci.token_id = st.id
            ci.from_staff_id = current_staff['id']
            ci.save()
            return HttpResponse(json.dumps({"status": "ok", "msg": "已保存，并可在客户跟进中查看"}))
        else:
            # 都没有，那么返回错误信息
            return HttpResponse(json.dumps({"status": "fail",
                                            "msg": "电话、qq、email必须有其中一个"}))


@check_login
@check_roles(["课程顾问", ])
def follow_up_detail(request, cid):
    current_staff = request.session.get("user")
    ci = models.ClientInfo.objects.get(id=cid)
    history = models.ClientFollowUp.objects.filter(client_id=cid).order_by('-follow_time')
    areas = models.Area.objects.values('id', 'name').order_by('id')
    if request.method == 'GET':
        new_form = forms.FollowUp()
    else:
        new_form = forms.FollowUp(request.POST)
        if new_form.is_valid():
            result = request.POST.get("result")
            models.ClientFollowUp.objects.create(client_id=cid, staff_id=current_staff['id'], result=result)
            new_form = forms.FollowUp()
    return render(request, "app/followup-detail.html", {"ci": ci,
                                                        "history": history,
                                                        "new_form": new_form,
                                                        "areas": areas,})


@check_login
@check_roles(["课程顾问", ])
def new_client(request):
    current_staff = request.session.get("user")
    if request.method == 'GET':
        new_form = forms.ClientInfoForm()
    else:
        new_form = forms.ClientInfoForm(request.POST)
        if new_form.is_valid():
            obj = new_form.save(commit=False)
            obj.source = "manual"
            obj.from_staff_id = current_staff['id']
            obj.save()
            return render(request, "app/new-clientinfo-success.html")
    return render(request, "app/new-clientinfo.html", {"new_form": new_form})


@check_login
@check_roles(["课程顾问", ])
def no_more_follow(request):
    current_staff = request.session.get("user")
    if request.method == 'POST':
        cid = request.POST.get("cid")
        reason = request.POST.get("reason", "未填写原因")

        # 找到对应的客户，并且dont_follow要为False，避免重复操作
        ci = get_object_or_404(models.ClientInfo, id=cid, dont_follow=False)

        # 设置该客户的不再跟进为真
        ci.dont_follow = True
        ci.save()

        # 添加记录
        cfu = models.ClientFollowUp()
        cfu.client_id = cid
        cfu.staff_id = current_staff['id']
        cfu.result = "不再跟进该客户。\n" + reason
        cfu.save()

        return HttpResponse(json.dumps({"status": "ok"}))


# AJAX获取指定校区的所有课程
def load_courses(request, area_id):
    courses = models.Course.objects.filter(area_id=area_id).values('id', 'name', 'volume', )
    return HttpResponse(json.dumps(list(courses)))


# 安排客户参加试听课程
def exp_course(request):
    current_staff = request.session.get("user")
    if request.method == 'POST':
        try:
            client_id = request.POST.get("client_id")
            course_id = request.POST.get("course_id")
            course = models.Course.objects.get(id=course_id)
            area_id = request.POST.get("area_id")
            client = get_object_or_404(models.ClientInfo, id=client_id)
            new_student = models.StudentInfo()
            new_student.client_id = client_id
            new_student.name = client.name
            new_student.phone = client.phone
            new_student.email = client.email
            new_student.area_id = area_id
            new_student.status = models.StudentStatus.objects.get(name="未报名")
            new_student.save()
            new_student.courses.add(course)

            # 添加记录
            cfu = models.ClientFollowUp()
            cfu.client_id = client_id
            cfu.staff_id = current_staff['id']
            cfu.result = "已安排该客户试听 {} 第{}期".format(course.name, course.volume)
            cfu.save()
            return HttpResponse(json.dumps({"status": "ok"}))
        except Exception as e:
            return HttpResponse(json.dumps({"status": "fail", "msg": str(e)}))
