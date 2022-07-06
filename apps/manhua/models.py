from django.db import models

# Create your models here.
from conf.config import IMAGES_DOMAIN

# 分类
class Category(models.Model):
    name = models.CharField('分类名称', max_length=50)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = '漫画分类'
        verbose_name_plural = '漫画分类'

class Books(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    name = models.CharField('名称', max_length=255, db_index=True)
    author = models.CharField('作者', max_length=50, db_index=True, default='佚名')
    free_flag = models.BooleanField('是否免费', default=False)
    keywords = models.CharField('标签', max_length=255, default='', null=True)
    description = models.CharField('描述', max_length=255, default='', null=True)
    status_choices = (
        ('serialized', '連載中'),
        ('finish', '已完結'),

    )
    status = models.CharField('状态', max_length=20, choices=status_choices, default='serialized')
    onsale_choices = (
        ('on_sale', '銷售中'),
        ('finish', '已完結'),

    )
    onsale = models.CharField('状态', max_length=20, choices=onsale_choices, default='on_sale')
    cover_url = models.URLField('封面图片', default='', null=True)
    square_image = models.URLField('封面图片', default='', null=True)
    extension_url = models.URLField('封面图片', default='', null=True)
    read_count = models.IntegerField('阅读数', default=0)
    like_count = models.IntegerField('link数', default=0)
    recommend = models.BooleanField('是否推荐', default=False)
    tags = models.CharField('标签', max_length=255, default='', null=True)
    score = models.DecimalField('评分', max_digits=4, decimal_places=2, default=9.0, null=True)
    vip_free = models.BooleanField('vip是否免费', default=True, null=True)
    exclusive = models.BooleanField('独家', default=True)
    fresh = models.BooleanField('新品', default=True)
    h = models.BooleanField('h', default=True)
    update_day = models.IntegerField('更新时间', null=True)

    create_time = models.DateTimeField('添加时间', auto_now_add=True, null=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True)

    def __str__(self):
        return self.name

    def get_cover_url(self):
        if self.cover_url.startswith('/'):
            return f'{IMAGES_DOMAIN}{self.cover_url}'
        return self.cover_url.replace('image.dayi58.com', '9welkjsk3.yxsw888.com')

    def get_square_image(self):
        filename = self.square_image.split('/')[-1]
        return self.square_image.replace('image.dayi58.com', '9welkjsk3.yxsw888.com')

    def get_extension_url(self):

        if self.extension_url.startswith('/'):
            return f'{IMAGES_DOMAIN}{self.extension_url}'
        return self.extension_url.replace('image.dayi58.com', '9welkjsk3.yxsw888.com')




    class Meta:
        verbose_name = '漫画列表'
        verbose_name_plural = '漫画列表'


# 章节
class Chapter(models.Model):
    books = models.ForeignKey('Books', on_delete=models.CASCADE, related_name='chapter')
    title = models.CharField('章节名称', max_length=255, db_index=True)
    sequence = models.PositiveSmallIntegerField('章节排序', default=0)
    cover_url = models.URLField('封面图片', null=True)
    points = models.IntegerField('点数', default=0)
    org_points = models.IntegerField('点数', default=0)
    free_flag = models.BooleanField('是否免费', default=True)
    has_read = models.BooleanField('已阅读', default=False)
    has_purchase = models.BooleanField('是否购买', default=False)
    vip_free = models.BooleanField('VIP免费', default=True)
    create_time = models.DateTimeField('添加时间', auto_now_add=True, null=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True)
    display = models.BooleanField('是否显示', default=1)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '章节列表'
        verbose_name_plural = '章节列表'

# 图集列表
class Images(models.Model):
    chapter = models.ForeignKey('Chapter', related_name='images', on_delete=models.CASCADE)
    url = models.URLField('图片地址')
    sequence = models.PositiveSmallIntegerField('图片排序', default=0)
    width = models.IntegerField('宽度', default=720)
    height = models.IntegerField('高度', default=700)


    create_time = models.DateTimeField('添加时间', auto_now_add=True, null=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True)

    def __str__(self):
        return self.chapter.title


    def get_url(self):

        # 如果是外链地址， 优先替换为 111557 防止图片失效
        if self.url.startswith('https://9welkjsk3.yxsw888.com'):
            file_map = self.url.split('/')[-3:len(self.url.split('/'))]
            file_map.insert(0, 'https://images.111557.xyz')
            url = '/'.join(file_map)
            return url

        if self.url.startswith('/'):
            return f'{IMAGES_DOMAIN}{self.url}'

        if self.url.startswith('b'):
            return f'{IMAGES_DOMAIN}/{self.url}'

        return self.url.replace('9welkjsk3.yxsw888.com', 'images.111557.xyz')

    class Meta:
        verbose_name = '图片列表'
        verbose_name_plural = '图片列表'
