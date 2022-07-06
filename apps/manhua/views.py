from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db.models import Q
from django.forms.models import model_to_dict
from apps.manhua import models
from conf.config import ALL_FREE, TOP_BOOKS
from apps.manhua.crawler import start_chapter_update_images


try:
    from apps.users.models import RecentRead, BookShelf
except:
    pass

# 漫画首页
def manhua_index(request):
    # start_chapter_update_images()
    request.title = 'index'
    # 热门漫画
    read_books = models.Books.objects.filter().order_by('?')[:12]
    # 免费漫画
    free_books = models.Books.objects.filter(free_flag=1).order_by('-id')[:12]
    # 最新更新漫画
    books = models.Books.objects.filter().order_by('-update_time')[:12]
    # recommend = models.Books.objects.filter(id__in=[5012, 5000, 5031, 6467])
    result = {'books': books, 'read_books': read_books, 'free_books': free_books, 'top_manhua': TOP_BOOKS}
    return render(request, 'manhua/index.html', result)


# 漫画详情
def manhua_comics(request, book_id):

    book_info = models.Books.objects.filter(id=book_id).first()

    chapters = models.Chapter.objects.filter(books_id=book_id, display=True).order_by('sequence')

    result = {'book_info': book_info, 'chapters': chapters}


    try:
        # 判断 是否已收藏
        if BookShelf.objects.filter(user_id=request.user_info.id, book_id=book_id).first(): result.update({'books_shelf': True})
    except:
        pass

    result.update({
        'is_free': ALL_FREE
    })

    return render(request, 'manhua/comics.html', result)

# 章节详情
def manhua_chapter(request, chapter_id):
    images = models.Images.objects.filter(chapter_id=chapter_id).order_by('sequence')
    if len(images) == 0: return HttpResponse('404x')
    book_info = images.first().chapter.books
    now_sequence = images.first().chapter.sequence

    # 判断是否登录
    if request.is_login:
        # 当前章节信息
        chapter_info = images.first().chapter
        # 加入已看记录, 先判断是否存在, 存在就更新为当前章节
        ret = RecentRead.objects.filter(user_id=request.user_info.id, chapter__books_id=chapter_info.books_id).first()
        if not ret :
            # pass
            RecentRead.objects.create(user_id=request.user_info.id, chapter_id=chapter_info.id)
        else:
            ret.chapter_id = chapter_info.id
            ret.save()


    prev_book = models.Chapter.objects.filter(books_id=book_info.id, sequence__lt=now_sequence).order_by('-sequence').first()
    next_book = models.Chapter.objects.filter(books_id=book_info.id, sequence__gt=now_sequence).order_by('sequence').first()

    result = {'images': images, 'image_info': images.first(), 'book_info': book_info, 'prev_book': prev_book,
              'next_book': next_book, 'views': True}

    # 全站收费 为否 且 用户未登录 且 章节收费的情况下
    if not ALL_FREE and not request.is_login and not images.first().chapter.free_flag:

        result.update({
            'images': images[:2],
            'views': False
        })

    # 全站收费 为否 且 用户已登录 且 章节收费 且 用户非VIP的情况下  这两个判断临时写 后期版本需要再优化
    if not ALL_FREE and request.is_login and not images.first().chapter.free_flag and not request.user_info.is_vip:
        result.update({
            'images': images[:2],
            'views': False
        })


    try:
        # 判断 是否已收藏
        if BookShelf.objects.filter(user_id=request.user_info.id, book_id=book_info.id).first(): result.update({'books_shelf': True})
    except:
        pass

    return render(request, 'manhua/chapter.html', result)

# 搜索页
def manhua_serach(request):
    return render(request, 'manhua/search.html')

# 搜索结果
def manhua_tag(request):
    keyword = request.GET.get('keyword', '')
    q = Q()
    q.add(Q(name__icontains=keyword), Q.AND)
    order_by = ['-id']
    if keyword == '已完结':
        q = Q(status='finish')

    if keyword == '热门推荐':
        order_by = ['-read_count', '-id']
        q = Q()

    if keyword == '最近更新':
        order_by = ['-update_time', '-id']
        q = Q()

    if keyword == '免费漫画':
        q = Q(free_flag=True)

    serach_books = models.Books.objects.filter(q).order_by(*order_by)
    result = {'serach_books': serach_books, 'keyword': keyword}
    return render(request, 'manhua/tag.html', result)





def index(request):
    data_list = models.Books.objects.filter()
    _data_list = []
    for data in data_list:
        _data = {
            'id': data.id,
            'name': data.name,
            'author': data.author,
            'status': data.status
        }
        _data_list.append(_data)
    return JsonResponse({'code': 200, 'msg': '获取成功', 'data': {'items': _data_list}})



def get_chapter(request, book_id=0):
    book_info = models.Books.objects.filter(id=book_id).first()
    if not book_info:
        return JsonResponse({'code': 404, 'msg': '数据不存在' })

    data_list = models.Chapter.objects.filter(books_id=book_info.id).order_by('sequence')
    _data_list = []
    for foo in data_list:
        data = {
            'id': foo.id,
            'name': foo.title,
            'cover_url': foo.cover_url,
            'image_list': list(foo.images.order_by('sequence').values_list('url', flat=True))
        }
        _data_list.append(data)

    return JsonResponse({'code': 200, 'msg': '获取成功', 'data': {'items': _data_list}})
