from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.conf import settings
from apps.manhua.crawler import update_books, update_books_meto
from apps.users.models import Account

import datetime

class Command(BaseCommand):
    help = '更新漫画列表'

    def handle(self, *args, **options):
        self.check_vip()
        update_books()
        self.stdout.write(self.style.SUCCESS('  漫画更新成功'))

    # 检测会员是否到期
    def check_vip(self):
        Account.objects.filter(is_vip=True, expire_time__lte=datetime.datetime.now()).update(is_vip=False)