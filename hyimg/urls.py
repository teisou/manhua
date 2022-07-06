"""hyimg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.manhua import views as mh_views

urlpatterns = [
    path('hyadmin/', admin.site.urls),

    path('', mh_views.manhua_index, name="manhua_index"),
    path('get/comics/<int:book_id>', mh_views.manhua_comics, name="manhua_comics2"),
    path('comics/<int:book_id>', mh_views.manhua_comics, name="manhua_comics"),
    path('chapter/<int:chapter_id>', mh_views.manhua_chapter, name="manhua_chapter"),
    path('serach.html', mh_views.manhua_serach, name="manhua_serach"),
    path('tag', mh_views.manhua_tag, name="manhua_tag"),
    path('get/chapter/<int:book_id>', mh_views.get_chapter, name="get_chapter"),


    path('user/', include('apps.users.urls'))
    # 开发模式
    # path('dev-api/manhua/', include('apps.manhua.urls')),

]
