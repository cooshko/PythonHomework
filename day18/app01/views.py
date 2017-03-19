from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.db.models import F, Q
from .models import *
from .forms import *
from backend.json_encoder import *
import json, datetime, hashlib, random


# 检查登录装饰器
def check_login(func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("is_login", False):
            current_user = request.session.get("current_user")
            User.objects.filter(id=current_user['id']).update(is_login=True, last_login=timezone.now())
            return func(request, *args, **kwargs)
        else:
            return HttpResponse(json.dumps({'status': 'fail', 'error': '请先登录'}))
            # return render(request,
            #               'app01/upload_result.html',
            #               {'result': json.dumps({'status': 'fail', 'error': '请先登录'})})

    return wrapper


# 首页重定向
def redirect2index(request):
    return redirect("/app01/")


# 首页
def index(request):
    visible_catalog = Catalog.objects.filter(visible=True).values()
    enable_catalog = visible_catalog.filter(enable=True).values()
    return render(request, "app01/index.html", {
        "is_login": request.session.get("is_login"),
        "user": request.session.get("current_user"),
        "visible_catalog": visible_catalog,
        "enable_catalog": enable_catalog,
    })


# 用户注册
def register(request):
    # 注册的URL
    if request.method == 'POST':
        reg_frm = RegisterFrm(data=request.POST)
        if reg_frm.is_valid():
            cd = reg_frm.cleaned_data
            # 验证码比对
            vcode_from_client = cd.get("verify_code", "")
            vcode_in_session = request.session.get("verify_code")
            if vcode_from_client and vcode_in_session and vcode_from_client.upper() == vcode_in_session.upper():
                # 验证码比对通过
                new_user = reg_frm.save(commit=False)
                password2 = cd.get("password2")
                m = hashlib.md5()
                m.update(password2.encode())
                new_user.password = m.hexdigest()
                new_user.display_name = cd.get("login_name")
                new_user.email = cd.get("email")
                # new_user.last_login = datetime.datetime.now()
                new_user.last_login = timezone.now()
                new_user.last_ip = request.META.get("REMOTE_ADDR")
                new_user.save()
                # request.POST['verify_code'] = ""
                return HttpResponse(json.dumps({'status': 'ok'}))
            return HttpResponse(json.dumps({'status': 'fail', 'msg': '验证码不正确'}))
        else:
            return HttpResponse(reg_frm.errors.as_json())


# 用户注册时，检查提交的数据是否占用
def check_exist(request):
    # 检查是否已存在相同的值
    if request.method == 'POST':
        check_type = request.POST.get("check_type")
        value = request.POST.get("check_value")
        parameter = {check_type: value}
        count = User.objects.filter(**parameter).count()
        if count > 0:
            return HttpResponse(json.dumps({'status': 'fail', 'msg': 'exist'}))
        else:
            return HttpResponse(json.dumps({'status': 'ok'}))


def verify_code(request):
    """生成验证码图片"""
    from backend import check_code as CheckCode  # 该check_code是老师的验证码插件
    from io import BytesIO  # BytesIO是内存Stream，用于存取二进制数据，可当文件handler用
    codeImg, strs = CheckCode.create_validate_code()
    request.session['verify_code'] = strs
    stream = BytesIO()
    codeImg.save(stream, 'png')
    return HttpResponse(stream.getvalue(), r'image/png')


# 登陆
def login(request):
    # 登录视图，检查用户名 + 密码md5 ，不通过返回fail+验证失败
    # 检查enable，不通过返回fail + 用户已停用
    # 全部通过则返回ok+用户昵称+用户头像
    if request.method == 'POST':
        ret = {'status': '',
               'error': '',
               'display_name': '',
               'head_pic': ''}
        login_name = request.POST.get("login_name")
        password = request.POST.get("password")
        if login_name and password:
            # 将密码转md5
            m = hashlib.md5()
            m.update(password.encode())
            password_md5 = m.hexdigest()

            # 获取用户对象
            user = User.objects.filter(login_name=login_name, password=password_md5).first()
            if user:
                # 检查是否无效
                if user.enable:
                    # 有效
                    # 将用户信息登记到session中
                    request.session['is_login'] = True
                    request.session['current_user'] = {
                        'id': user.id,
                        'login_name': user.login_name,
                        'display_name': user.display_name,
                    }

                    # 返回验证通过信息+用户昵称+头像url到客户端
                    ret['status'] = 'ok'
                    ret['display_name'] = user.display_name
                    ret['head_pic'] = settings.STATIC_URL + r'img/head/' + (user.head_pic or 'mxcp_320x320.jpg')
                else:
                    ret['status'] = 'fail'
                    ret['error'] = '该用户已停用'
            else:
                ret['status'] = 'fail'
                ret['error'] = '用户名或密码不正确'
        else:
            ret['status'] = 'fail'
            ret['error'] = '用户名或者密码不能为空'
        return HttpResponse(json.dumps(ret))


# 登出
def logout(request):
    request.session['is_login'] = False
    request.session['current_user'] = {}
    return HttpResponse(json.dumps({'status': 'ok'}))


# 用户上传图片
@check_login
def upload(request):
    if request.method == 'POST':
        # 上传文件，暂时只支持jpg、png，且体积在4M以下，
        # 计算文件的md5，
        ret = {'status': '',
               'msg': '',
               'error': '',
               'link': '',
               }
        img = request.FILES.get("publish_file")
        if img.size > settings.UPLOAD_PARAMETERS['SIZE_LIMIT']:
            ret['status'] = 'fail'
            ret['error'] = '文件大小超过限制。当前限制是：' + settings.UPLOAD_PARAMETERS['SIZE_LIMIT'] + '，您的文件大小是：' + img.size
        elif img.content_type not in settings.UPLOAD_PARAMETERS['FILE_TYPE']:
            ret['status'] = 'fail'
            ret['error'] = '不接受该文件类型。'
        else:
            # 获取后缀
            file_ext = os.path.splitext(img.name)[1] if '.' in img.name else 'jpg'

            # 生成临时文件路径
            letters = 'abcdefghijklmnopqrstuvwxyz0123456789'  # 用于生成临时文件名
            tmp_filename = ''
            tmp_file_path = ''
            while True:
                # 如果同名的临时文件已存在，则重新再取
                tmp_filename = ''.join(random.sample(letters, 8))
                tmp_file_path = os.path.join(settings.UPLOAD_PARAMETERS['TMP_PATH'], tmp_filename)
                if not os.path.exists(tmp_file_path):
                    break

            # 获取文件数据
            received_size = 0
            m = hashlib.md5()
            with open(tmp_file_path, 'wb') as fh:
                for chunk in img.chunks():
                    # b''.join([file_obj, chunk])
                    fh.write(chunk)
                    m.update(chunk)
                    received_size += len(chunk)

            # 接收完毕
            if received_size == img.size:
                # 读取到全部数据后，计算md5
                hash_value = m.hexdigest()

                # 移动文件，并使用md5值做新文件名
                new_file_name = hash_value + file_ext
                new_file_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'upload', new_file_name)
                if os.path.isfile(new_file_path):
                    # 新目标文件已经存在，无需覆盖，并清理临时文件
                    os.remove(tmp_file_path)
                else:
                    # 如果目标新文件不存在，则将临时文件移动过去并重命名
                    os.rename(tmp_file_path, new_file_path)

                ret['status'] = 'ok'
                ret['msg'] = new_file_name
                ret['link'] = settings.STATIC_URL + 'img/upload/' + new_file_name
            else:
                # 未获取到完整的数据
                ret['status'] = 'fail'
                ret['error'] = '数据不完整，请重新上传'
        return HttpResponse(json.dumps(ret))


# 用户发布内容
@check_login
def publish(request):
    """ 用户发布内容 """
    if request.method == 'POST':
        user_id = request.session.get("current_user")['id']
        pub_text = request.POST.get("pub_text")
        catalog_id = request.POST.get("catalog")
        img_link = request.POST.get("img_link", "")
        post = Post()
        post.catalog_id = catalog_id
        post.user_id = user_id
        post.img_link = img_link
        post.content = pub_text
        post.save()
        Like.objects.create(user_id=user_id, post_id=post.id)
        ret = {'status': 'ok'}
        return HttpResponse(json.dumps(ret))


# 根据用户提交的类别catalog来读取帖子
def posts(request):
    if request.method == 'GET':
        is_login = request.session.get("is_login", False)
        catalog_id = int(request.GET.get("catalog", 0))  # 如果URL参数中没有catalog，则为0，代表全部的意思
        page = int(request.GET.get("page", 1))  # 如果URL参数中没有page，视为从第一页开始取
        if page <= 0:
            # 如果page是0或者负数，则视为第一页
            page = 1
        start = (page - 1) * settings.POSTS_PARAMETERS.get('LIMIT', 10)  # 根据page和LIMIT获得起始位
        end = page * settings.POSTS_PARAMETERS.get('LIMIT', 10)  # 获得终结位
        if catalog_id == 0:
            post_list = Post.objects.all().order_by("-id")[start:end]  # 获取全部帖子，并逆序排序
            posts_count = Post.objects.all().count()
        else:
            # post_list = Post.objects.filter(catalog_id=catalog_id).all().order_by("-id")[start:end]
            post_list = Catalog.objects.filter(id=catalog_id, visible=True).first() \
                            .posts.all().order_by("-id")[start:end]
            posts_count = Catalog.objects.filter(id=catalog_id, visible=True).first() \
                .posts.all().count()
        page_count, mod = divmod(posts_count, 5)
        if mod > 0:
            page_count += 1
        ret = {}
        ret['status'] = 'ok'
        ret['data'] = {}
        ret['data']['page_count'] = page_count
        ret['data']['current_page'] = page if page <= page_count else "超出范围了！"
        ret['data']['current_catalog'] = catalog_id
        ret['data']['posts'] = list(post_list.values("id",
                                                     "user__display_name",
                                                     "catalog_id",
                                                     "catalog__name",
                                                     "create_on",
                                                     "content",
                                                     "top",
                                                     "top_time",
                                                     "like_count",
                                                     "comment_count",
                                                     "img_link"))

        # 判断当前用户是否赞
        if is_login:
            current_user = request.session.get("current_user")
            current_user_likes = Like.objects.filter(user_id=current_user['id']).values_list("post_id", flat=True)
        else:
            current_user_likes = []
        for post in ret['data']['posts']:
            post['like'] = post['id'] in current_user_likes

        return HttpResponse(json.dumps(ret, cls=DateTimeJSONEncoder))


# 点赞功能，如果用户未赞过，则点赞；否则，取消赞
@check_login
def like_post(request):
    ret = {'status': 'ok'}
    if request.method == 'GET':
        post_id = request.GET.get("post")
        user_id = request.session.get("current_user")['id']
        like_record = Like.objects.filter(user_id=user_id, post_id=post_id).all()
        if like_record:
            # 已赞过,取消赞
            like_record.delete()
            ret['msg'] = 'unliked'
            Post.objects.filter(id=post_id).update(like_count=F("like_count") - 1)
        else:
            # 未赞过，赞一下
            Like.objects.create(user_id=user_id, post_id=post_id)
            Post.objects.filter(id=post_id).update(like_count=F("like_count") + 1)
            ret['msg'] = 'liked'

        return HttpResponse(json.dumps(ret))


@check_login
def post_comment(request):
    ret = {'status': 'ok'}
    if request.method == 'POST':
        user_id = request.session.get("current_user")['id']
        post_id = request.POST.get("post")
        post = get_object_or_404(Post, id=post_id)
        comment_text = request.POST.get("comment_text")
        reply_to = request.POST.get("reply_to")
        Comment.objects.create(user_id=user_id, post=post, content=comment_text, reply_to=reply_to)
        post.comment_count += 1
        post.save()
        return HttpResponse(json.dumps(ret))


def get_comments(request):
    ret = {'status': 'ok'}
    if request.method == 'GET':
        post_id = request.GET.get("post")
        post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post=post).values("id",
                                                            "user_id",
                                                            "user__display_name",
                                                            "create_on",
                                                            "content",
                                                            "reply_to").order_by('id')
        ret['data'] = list(comments)
        return HttpResponse(json.dumps(ret, cls=DateTimeJSONEncoder))


# 获取在线用户
@check_login
def get_online_users(request):
    current_user = request.session.get("current_user")
    current_user_id = current_user.get("id")
    current_time = timezone.now()
    td = datetime.timedelta(**settings.LOGIN_PARAMETERS['ONLINE_INTERVAL'])
    users = User.objects.exclude(id=current_user_id, ).filter(is_login=True,
                                                              last_login__gte=(
                                                                  current_time + td)
                                                              ).values("id", "head_pic", "display_name",)
    users_list = list(users)
    return HttpResponse(json.dumps({
        'status': 'ok',
        'data': users_list
    }))
