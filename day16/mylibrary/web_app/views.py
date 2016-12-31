from django.shortcuts import render, HttpResponse, redirect
from django.db.utils import IntegrityError
import json, os, hashlib
# from day16.mylibrary.web_app import models
from web_app import models
from mylibrary import settings
from PIL import Image


def redirect_index(request):
    return redirect("/web/")


def index(request):
    recent = get_recent()
    books = get_books()
    publisher_list = get_publishers()
    catalog_list = get_catalog()
    return render(request, 'index.html', {
        'recent': recent,
        'books': books,
        'publisher_list': publisher_list,
        'catalog_list': catalog_list,
    })


def get_recent():
    """
    获取最近添加的书
    :return:
    """
    recent = models.BookInfo.objects.all().order_by('-create_time').first()
    return recent


def get_books(page=0, limit=5):
    """
    获取书的信息，但一次默认只能获取5本
    :param page:
    :param limit:
    :return:
    """
    offset = page * limit
    books = models.BookInfo.objects.all()[offset:offset + limit]
    return books
    # books = []
    # for book in models.BookInfo.objects.all():
    #     temp = {
    #         'name': str(book.name),
    #         'publisher': str(book.publisher),
    #         'version': str(book.version),
    #         'cover': str(book.cover),
    #         'description': str(book.description),
    #         'catalog': str(book.catalog),
    #         # 'create_time': book.create_time,
    #         'update_time': str(book.update_time),
    #         'authors': list(book.authors.all().values('name')),
    #     }
    #     books.append(temp)


# def demo_add(request):
    # catalog = models.CatalogInfo.objects.create(name="教程")
    # author1 = models.AuthorInfo.objects.create(name="田果")
    # author2 = models.AuthorInfo.objects.create(name="刘丹宁")
    # publisher = models.PublisherInfo.objects.create(name="人民邮电出版社")
    # book = models.BookInfo.objects.create(
    #     name="CCNP SWITCH学习指南",
    #     publisher=publisher,
    #     catalog=catalog,
    #     version=2,
    # )
    # book.authors.add(author1)
    # book.authors.add(author2)
    # book = models.BookInfo.objects.get(name="CCNP SWITCH学习指南")
    # book.cover = r'/static/book-gallery/CCNP SWITCH学习指南.png'
    # book.save()

    # 用filter返回QuerySet，再使用update，这种做法的好处是filter总是会返回而不报错，而get匹配不到的话会报错
    # book = models.BookInfo.objects.filter(name="CCNP SWITCH学习指南")
    # print(book.count())
    # book.update(cover=r'/static/book-gallery/CCNP SWITCH学习指南.png')
    # return HttpResponse('OK')


def get_publishers(request=None):
    """
    获取出版社信息
    :param request:
    :return:
    """
    if request:
        # 保留功能
        pass
    else:
        ret = list(models.PublisherInfo.objects.all().values())
    return ret


def get_catalog(request=None):
    """
    获取类目信息
    :param request:
    :return:
    """
    if request:
        # 保留功能
        pass
    else:
        ret = list(models.CatalogInfo.objects.all().values())
    return ret


def edit_book(request):
    """
    编辑书本信息，包括了增删改
    :param request:
    :return:
    """
    func_map = {
        'add_book': add_book,
        'del_book': del_book,
        'modify_book': modify_book,
    }
    if request.method == 'POST':
        data = request.POST
        action = data.get('action')
        if action in func_map:
            ret = func_map[action](data)
        else:
            ret = False, "没有此方法"
        return HttpResponse(json.dumps(ret))


def upload_cover(request):
    if request:
        # 写入原文件，文件名以md5值开头
        f = request.FILES['cover']
        origin_path = os.path.join(settings.BASE_DIR, settings.STATICFILES_DIRS[0], 'upload')
        origin_fdata = b''
        for content in f.chunks():
            origin_fdata += content
        m = hashlib.md5()
        m.update(origin_fdata)
        origin_fext = f.name.split('.')[-1]
        origin_fname = m.hexdigest() + '.' + origin_fext
        origin_fpath = os.path.join(origin_path, origin_fname)
        with open(origin_fpath, 'wb') as fp:
            fp.write(origin_fdata)

        new_path = os.path.join(settings.BASE_DIR, settings.STATICFILES_DIRS[0], 'book-gallery')
        new_fname = resize_image(origin_fpath, new_path)
        uri = settings.STATIC_URL + r'book-gallery/' + new_fname
        ret = json.dumps((True, uri))
    else:
        ret = json.dumps((False, "unknown request"))
    return HttpResponse(ret)


def resize_image(img_fp, new_path):
    origin_fname = os.path.basename(img_fp)
    new_fpath = os.path.join(new_path, origin_fname)
    im = Image.open(img_fp)
    new_size = 140, 200
    im.thumbnail(new_size, Image.ANTIALIAS)
    im.save(new_fpath)
    return os.path.basename(new_fpath)


def add_publisher(iName):
    """
    添加出版社
    :param iName: 出版社名称，可以是字符串也可以是字符串列表
    :return: 如果iName是字符串，则返回(bool, oPublisher_id)
              如果iName是列表，则返回(bool, oPublishers_id_list)
              如果都不是，则返回(False, "iName应该是列表或者字符串")
    """
    iName = iName.strip()
    if iName:
        ret = (False, "iName应该是列表或者字符串")
        if isinstance(iName, str):
            publisher_id = models.PublisherInfo.objects.create(name=iName)
        elif isinstance(iName, list):
            publishers_id_list = []
            for name in iName:
                publisher_id = models.PublisherInfo.objects.create(name=iName)
    else:
        ret = (False, "iName不能为空")
    return ret


def add_book(data):
    try:
        new_book = models.BookInfo()
        new_book.name = data.get('name')
        new_book.version = data.get('version')
        new_book.cover = data.get('cover_uri')
        new_book.description = data.get('description')

        # 外键的处理
        catalog_id = data.get('catalog')
        new_book.catalog = models.CatalogInfo.objects.filter(id=catalog_id).first()
        publisher_id = data.get('publisher')
        new_book.publisher = models.PublisherInfo.objects.filter(id=publisher_id).first()

        # 先保存一下
        new_book.save()

        # 检查作者是否已经存在
        authors_str = data.get('authors')
        authors = None
        author_obj_list = []
        if authors_str:
            authors_str = authors_str.strip()
            if authors_str:
                authors = authors_str.split()
                for author in authors:
                    author_obj = models.AuthorInfo.objects.filter(name=author).first()
                    if author_obj:
                        author_obj_list.append(author_obj)
                    else:
                        new_author = models.AuthorInfo()
                        new_author.name = author
                        new_author.save()
                        author_obj_list.append(new_author)
        for author_obj in author_obj_list:
            new_book.authors.add(author_obj)
        ret = True, "保存成功！"
        return json.dumps(ret)
    except IntegrityError as e:
        if str(e).startswith('UNIQUE constraint failed'):
            ret = False, "该书名已存在，不能重复创建"
        else:
            ret = False, str(e)
        return json.dumps(ret)


def del_book(data):
    pass

def modify_book(data):
    pass