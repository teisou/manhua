
from django.urls import path, include
from apps.users import views



urlpatterns = [

    # 阅读记录列表
    path('books/read', views.RecentRead, name='RecentRead'),

    # 删除阅读记录
    path('books/read/delete', views.ReadDelete, name='ReadDelete'),

    #收藏列表
    path('books/shelf', views.BookShelf, name='BookShelf'),

    # 点击收藏
    path('collect/comic/<int:book_id>', views.collect_comic, name='collect_comic'),

    path('account', views.Account, name='Account'),

    path('login', views.Login, name='Login'),
    path('vip', views.Vip, name='vip'),
    path('logout', views.user_logout, name='user_logout'),
]
