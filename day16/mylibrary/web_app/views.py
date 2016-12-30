from django.shortcuts import render, HttpResponse
import json
# from day16.mylibrary.web_app import models
from web_app import models


# Create your views here.
def index(request):
    return render(request, 'index.html')


def get_all_books(request, start=0, limit=5):
    all_book = []
    # print(models.BookInfo.objects.all().values())
    for book in models.BookInfo.objects.all():
        temp = {
            'name': str(book.name),
            'publisher': str(book.publisher),
            'version': str(book.version),
            'cover': str(book.cover),
            'description': str(book.description),
            'catalog': str(book.catalog),
            # 'create_time': book.create_time,
            'update_time': str(book.update_time),
            'authors': list(book.authors.all().values('name')),
        }
        all_book.append(temp)
    return HttpResponse(json.dumps(all_book))


def demo_add(request):
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
    book = models.BookInfo.objects.filter(name="CCNP SWITCH学习指南")
    print(book.count())
    # book.update(cover=r'/static/book-gallery/CCNP SWITCH学习指南.png')
    return HttpResponse('OK')


