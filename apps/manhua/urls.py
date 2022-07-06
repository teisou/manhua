"""
用户模块 路由
"""

# from django.urls import path, include
# from . import views
#
#
# # app_name = 'images'
#
#
# urlpatterns = [
#     # 获取首页数据
#     path('get/books', views.index, name="get_index_view"),
#     path('get/index', views.manhua_index, name="manhua_index"),
#     path('get/comics/<int:book_id>', views.manhua_comics, name="manhua_comics"),
#     path('chapter/<int:chapter_id>', views.manhua_chapter, name="manhua_chapter"),
#     path('serach.html', views.manhua_serach, name="manhua_serach"),
#     path('tag', views.manhua_tag, name="manhua_tag"),
#     path('get/chapter/<int:book_id>', views.get_chapter, name="get_chapter"),
#
#     path('user/', include('apps.users.urls'))
#
# ]

import os

from urllib.parse import urlparse

url = urlparse('https://image2.dayi58.com/959b6772eed86198a83e416cc50cabcb/60040b29/banner/8c878200-404b-4a91-9974-d704edde272c.png')
print(url)