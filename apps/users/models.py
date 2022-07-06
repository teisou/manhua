from django.db import models

from apps.manhua.models import Books, Chapter

# Create your models here.
class Account(models.Model):
    username = models.CharField('用户名', max_length=50, db_index=True, unique=True)
    password = models.CharField('密码', max_length=50)
    phone = models.CharField('手机号码', max_length=15, null=True, default='')
    email = models.EmailField('邮件地址', default='', blank=True)
    is_vip = models.BooleanField('是否VIP', default=False)

    create_time = models.DateTimeField('添加时间', auto_now_add=True, null=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True)
    expire_time = models.DateTimeField('VIP到期时间', null=True, default=None, blank=True)


# 历史记录
class RecentRead(models.Model):
    user = models.ForeignKey('Account', on_delete=models.CASCADE, null=True)
    # book_id = models.IntegerField('图书id', db_index=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True)
    create_time = models.DateTimeField('添加时间', auto_now_add=True, null=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True)

# 收藏
class BookShelf(models.Model):
    user = models.ForeignKey('Account', on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)

    create_time = models.DateTimeField('添加时间', auto_now_add=True, null=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, null=True)


# 激活码
class Coupon(models.Model):
    code = models.CharField('优惠码', max_length=32, db_index=True, unique=True)
    user = models.ForeignKey('Account', on_delete=models.SET_NULL, null=True)
    status_choices = (
        (1, '未使用'),
        (2, '已使用'),
        (3, '已到期')
    )
    status = models.PositiveSmallIntegerField('优惠类型', choices=status_choices, default=1)

    days = models.IntegerField('激活天数', default=0)

    create_time = models.DateTimeField('创建时间', null=True, auto_now_add=True)
    update_time = models.DateTimeField('更新时间', null=True, auto_now=True)
    expire_time = models.DateTimeField('失效时间', null=True, default=None, blank=True)

    def __str__(self):
        return self.code

    class Meta:
        # db_table = 'doors_node_group'
        verbose_name = "优惠管理"
        verbose_name_plural = verbose_name