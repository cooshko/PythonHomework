from django.db import models


class MyCommon(object):
    def __str__(self):
        ret = getattr(self, 'name', "noname")
        return ret


class AuthorInfo(MyCommon, models.Model):
    # 作者信息表
    name = models.CharField(max_length=64, unique=True)


class PublisherInfo(MyCommon, models.Model):
    # 出版社
    name = models.CharField(max_length=64, unique=True)


class BookInfo(MyCommon, models.Model):
    # 书本信息
    name = models.CharField(max_length=64, unique=True)          # 书名
    publisher = models.ForeignKey("PublisherInfo")  # 出版社
    version = models.PositiveIntegerField()         # 书的版本
    cover = models.ImageField(null=True)            # 封面图片路径
    description = models.TextField(null=True)       # 书的说明
    catalog = models.ForeignKey("CatalogInfo")      # 图书分类
    create_time = models.DateTimeField(auto_now_add=True)   # 本记录创建时间
    update_time = models.DateTimeField(auto_now=True)       # 修改时间
    authors = models.ManyToManyField(AuthorInfo)            # 作者信息（多对多，一本书可以多个作者，一个作者可以有多本书）

class CatalogInfo(MyCommon, models.Model):
    # 图书分类
    name = models.CharField(max_length=64, unique=True)
