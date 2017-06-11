from django.db import models


class Catalog(models.Model):
    # 模块分类
    name = models.CharField(max_length=32, unique=True)
    enable = models.BooleanField(default=True)   # 是否开放发帖等功能
    visible = models.BooleanField(default=True)  # 是否可见

    def __str__(self):
        return self.name


class User(models.Model):
    # 用户表
    login_name = models.CharField(max_length=32, unique=True, verbose_name="用户名", error_messages={
        'unique': "用户名已被占用"
    })
    password = models.CharField(max_length=32,)
    display_name = models.CharField(max_length=32, unique=True, error_messages={
        'unique': "昵称已被占用"
    })
    email = models.EmailField(unique=True, error_messages={
        'unique': "邮箱已被注册"
    })
    enable = models.BooleanField(default=True)  # 是否启用，如果False，将不允许登录
    create_on = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField()
    last_ip = models.GenericIPAddressField()
    head_pic = models.TextField(null=True, blank=True)
    is_login = models.BooleanField(default=False)

    def __str__(self):
        return self.login_name


class Post(models.Model):
    # 帖子表
    # title = models.CharField(max_length=60)
    user = models.ForeignKey('User', related_name='posts')
    create_on = models.DateTimeField(auto_now_add=True)
    lock = models.BooleanField(default=False)   # 如果帖子被锁定将无法进行评论
    catalog = models.ForeignKey('Catalog', related_name='posts')
    content = models.TextField()
    top = models.BooleanField(default=False)
    top_time = models.DateTimeField(null=True)
    like_count = models.PositiveIntegerField(default=1)
    comment_count = models.PositiveIntegerField(default=0)
    img_link = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.content


class Comment(models.Model):
    # 评论表
    user = models.ForeignKey('User', related_name='comments')
    post = models.ForeignKey('Post', related_name='comments')
    content = models.TextField()
    reply_to = models.PositiveIntegerField(null=True, blank=True)
    create_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


# class Upload(models.Model):
#     # 上传文件的信息表
#     user = models.ForeignKey('User', related_name='uploads')
#     post = models.ManyToManyField('Post', related_name='uploads')
#     fname = models.CharField(max_length=64)
#     fsize = models.PositiveIntegerField()
#     hash_value = models.CharField(max_length=32)
#     create_on = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.fname


class Like(models.Model):
    user = models.ForeignKey('User', related_name="likes")
    post = models.ForeignKey('Post', related_name="likes")

    class Meta:
        unique_together = (('user', 'post'),)



