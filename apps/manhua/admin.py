from django.contrib import admin

# Register your models here.


from .models import Category
from .models import Books
from .models import Chapter
from .models import Images

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('id', 'name', 'author', 'tags', 'create_time')

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)

@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    pass