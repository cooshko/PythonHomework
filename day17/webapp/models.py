from django.db import models
from django.db.models import functions
from django.contrib.auth.hashers import make_password, check_password
from django.utils.translation import ugettext_lazy as _


# 校区，一个学员或班级仅属于一个校区，但一个老师或顾问可能属于多个校区
class Area(models.Model):
    name = models.CharField(max_length=30, unique=True)
    address = models.TextField(null=True, blank=True)
    telephone = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.name


# Staff员工角色表，讲师\课程顾问，将来可以添加
# 一个人可以有多个角色
class StaffRole(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


# 员工状态代码表，在职、离职
class StaffStatus(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class TeacherManager(models.Manager):
    def get_queryset(self):
        role = StaffRole.objects.get(name='讲师')
        return super(TeacherManager, self).get_queryset().filter(roles=role, status__name='在职')


class AdvisorManager(models.Manager):
    def get_queryset(self):
        role = StaffRole.objects.get(name='课程顾问')
        return super(AdvisorManager, self).get_queryset().filter(roles=role)


# 员工表，包含老师和课程顾问
class StaffInfo(models.Model):
    objects = models.Manager()
    teachers = TeacherManager()
    advisors = AdvisorManager()
    sysname = models.CharField(max_length=30, unique=True, verbose_name='登录名')  # 系统名，用于登录
    cname = models.CharField(max_length=30, verbose_name='中文名')     # 中文名
    gender = models.CharField(max_length=3, choices=(('男', '男'), ('女', '女'), ), verbose_name='性别')
    phone = models.CharField(max_length=20, verbose_name='电话')
    password = models.CharField(_('password'), max_length=64)
    status = models.ForeignKey('StaffStatus', verbose_name='状态')
    # area = models.ManyToManyField('Area')   # 一个员工可以属于多个校区
    area = models.ForeignKey('Area', verbose_name='属区')   # 员工所属校区
    roles = models.ForeignKey('StaffRole', verbose_name='职位')     # 员工角色
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cname

    def set_password(self, raw_password):
        """暂不使用加密"""
        self.password = make_password(raw_password)


# 课程班级表，
# 一个同学或者老师可以属于多个课程
class Course(models.Model):
    name = models.CharField(max_length=64, verbose_name='课程名称')
    volume = models.PositiveIntegerField()  # 第几期
    start_time = models.DateField(null=True, blank=True)
    area = models.ForeignKey("Area")
    monitor = models.ForeignKey('StudentInfo', null=True, blank=True)  # 班长
    teachers = models.ManyToManyField('StaffInfo')      # 多个老师
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('name', 'volume', 'area'),)     # 课程名 + 期 + 校区 联合唯一

    def __str__(self):
        return self.name


# 学员状态代码表，未报名前,报名后,毕业老学员，将来可以添加
class StudentStatus(models.Model):
    name = models.CharField(max_length=30, unique=True)
    def __str__(self):
        return self.name


# 学员表
class StudentInfo(models.Model):
    area = models.ForeignKey(Area)
    name = models.CharField(max_length=64)
    password = models.CharField(max_length=256, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    gender = models.CharField(choices=(('男', '男'), ('女', '女'), ), max_length=3, null=True, blank=True)
    phone = models.CharField(max_length=20)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    # updated_by = models.ForeignKey('StaffInfo')
    status = models.ForeignKey('StudentStatus')     # 状态：未报名前,报名后,毕业老学员
    courses = models.ManyToManyField('Course', blank=True)      # 多门课程
    client = models.ForeignKey('ClientInfo', null=True, blank=True, related_name="student")        # 客户编号

    class Meta:
        unique_together = (('name', 'gender', 'phone'),)

    def __str__(self):
        return self.name


# 成绩表
class CourseScore(models.Model):
    student = models.ForeignKey("StudentInfo")
    course = models.ForeignKey('Course')
    score = models.PositiveIntegerField()
    # test_at = models.DateTimeField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(StaffInfo)


# 出勤表
class Attendance(models.Model):
    course = models.ForeignKey('Course')
    student = models.ForeignKey('StudentInfo')
    attend_time = models.DateTimeField(auto_now_add=True)


# 客户信息表
class ClientInfo(models.Model):
    name = models.CharField(max_length=64)
    phone = models.CharField(max_length=64, null=True, blank=True)
    qq = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    token = models.OneToOneField('SessionTokens', blank=True, null=True)
    source = models.CharField(max_length=20, choices=(
        ('consult', '客户咨询'),
        ('manual', '手工添加')
    ), default='consult')
    create_at = models.DateTimeField(auto_now_add=True)
    dont_follow = models.BooleanField(default=False)
    from_staff = models.ForeignKey('StaffInfo', null=True, blank=True)


# 客户咨询记录
class ClientConsult(models.Model):
    session = models.ForeignKey('SessionTokens')     # 对应哪个会话
    msg = models.TextField()    # 消息内容
    from_client = models.BooleanField()     # 是否客户的消息，否代表客服的回答
    create_at = models.DateTimeField(auto_now_add=True)


# 咨询会话令牌，访客第一次访问时，在此表生成一个令牌，每次POST提交咨询内容时必须带有有效令牌
class SessionTokens(models.Model):
    token = models.CharField(max_length=64, unique=True)
    client_ip = models.GenericIPAddressField()
    source = models.CharField(max_length=20, default="web")    # 咨询来源
    staff = models.ForeignKey('StaffInfo', blank=True, null=True)
    active = models.BooleanField(default=True)
    client = models.ForeignKey("ClientInfo", null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)


# 后续跟进记录
class ClientFollowUp(models.Model):
    client = models.ForeignKey("ClientInfo")
    staff = models.ForeignKey("StaffInfo")
    follow_time = models.DateTimeField(auto_now_add=True)
    result = models.TextField()
