from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.forms.models import model_to_dict
from apps.users import models

from conf.config import VIP_CONTENT



import random, string, datetime

# 账户信息列表
def Account(request):
    request.title = 'account'
    if not request.is_login:
        # 如果没有登录就创建一个账号并登录
        try:
            uid = models.Account.objects.filter().order_by('-id').first().id + 1
        except:
            uid = 1

        password = 'p%s' % random.randint(10000, 99999)
        data = {
            'username': f'u{uid + 50000}',
            'password': md5(password)
        }
        user_info = models.Account.objects.create(**data)
        user_data = model_to_dict(user_info)
        user_data.update({
            'uid': user_info.id + 50000,
            'is_login': True
        })

        request.session['is_login'] = True
        request.session['user_data'] = user_data
        # request.session['user_info'] = user_info
        request.session['password'] = password
        request.user = user_data
        request.password = password

    return render(request, 'manhua/account.html')

# 登录账号
def Login(request):

    if request.method == 'GET':
        return render(request, 'manhua/login.html')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user_info = models.Account.objects.filter(username=username, password=md5(password)).first()
        if not user_info:

            return render(request, 'manhua/login.html', {"error_status": True})


        user_data = {
            'id': user_info.id,
            'uid': user_info.id + 50000,
            'username': user_info.username,
            'is_vip': user_info.is_vip,
            'is_login': True,
        }
        request.user_info = user_info
        request.session['is_login'] = True
        request.session['password'] = ''
        request.session['user_data'] = user_data
        return redirect('/user/account')

# vip 充值
def Vip(request):
    result = {
        'content': VIP_CONTENT
    }
    if request.method == 'GET':
        return render(request, 'manhua/vip.html', result)

    if request.method == 'POST':
        code = request.POST.get('code')
        code_info = models.Coupon.objects.filter(code=code).first()
        if not code_info:
            result.update({'error_status': '激活码不存在'})
            return render(request, 'manhua/vip.html', result)

        if code_info.status != 1:
            result.update({'error_status': '激活码已使用'})
            return render(request, 'manhua/vip.html', result)

        # 更新用户会员信息
        user_info = models.Account.objects.filter(id=request.user_info.id).first()

        # 更新激活码
        code_info.status = 2
        code_info.user_id = user_info.id
        code_info.save()

        try:
            new_time = user_info.expire_time + datetime.timedelta(days=code_info.days)
        except:
            new_time = datetime.datetime.now() + datetime.timedelta(days=code_info.days)

        user_info.expire_time = new_time
        user_info.is_vip = True
        user_info.save()

        result.update({'error_status': f'成功充值VIP {code_info.days} 天'})
        return render(request, 'manhua/vip.html', result)




# 注销登录
def user_logout(request):
    # 清空 session
    request.session.flush()
    return redirect('/')



# 书架
def BookShelf(request):
    request.title = 'books'
    try:
        data_list = models.BookShelf.objects.filter(user_id=request.user_info.id).order_by('-update_time')
    except:
        data_list = []
    # print(data_list)
    result = {
        'data_list': data_list
    }
    return render(request, 'manhua/books-shelf.html', result)

# 点击收藏
def collect_comic(request, book_id):
    try:
        shelf_info = models.BookShelf.objects.filter(user_id=request.user_info.id, book_id=book_id).first()
        if not shelf_info:
            # 如果不存在就收藏
            if models.BookShelf.objects.create(user_id=request.user_info.id, book_id=book_id):
                return JsonResponse({'code': 200, 'msg': '收藏成功', 'data': {'op': 'create'}})
            return JsonResponse({'code': 500, 'msg': '收藏失败', 'data': {'op': 'create'}})
        # 已经存在则删除收藏
        if models.BookShelf.objects.filter(user_id=request.user_info.id, book_id=book_id).delete():
            return JsonResponse({'code': 200, 'msg': '删除成功', 'data': {'op': 'delete'}})
        return JsonResponse({'code': 500, 'msg': '取消收藏失败', 'data': {'op': 'delete'}})
    except:
        return JsonResponse({'code': 500, 'msg': '操作失败', 'data': {'op': 'delete'}})


# 历史记录
def RecentRead(request):
    request.title = 'books'
    try:
        data_list = models.RecentRead.objects.filter(user_id=request.user_info.id).order_by('-update_time')
    except:
        data_list = []
    # print(data_list)
    result = {
        'data_list': data_list
    }
    return render(request, 'manhua/recent-read.html', result)

# 删除历史记录
def ReadDelete(request):
    try:
        ids = request.GET.get('ids', '').strip().split(',')
        models.RecentRead.objects.filter(user_id=request.user_info.id, id__in=ids).delete()
        return JsonResponse({'code': 200, 'info': '记录删除成功', 'status': True})
    except:
        return JsonResponse({'code': 500, 'info': '记录删除失败', 'status': False})


# 生成 md5
def md5(str):
    import hashlib
    m2 = hashlib.md5()
    m2.update(str.encode("utf-8"))
    return m2.hexdigest()