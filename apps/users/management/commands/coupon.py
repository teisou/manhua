from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.conf import settings

from apps.users.models import Coupon
from apps.users.views import md5
import uuid, time

class Command(BaseCommand):
    help = '生成/导出激活码'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('选择需要操作的类型！\n1, 创建激活码. \n2, 导出激活码'))
        _type = input('输入1或者2: ')
        if _type not in ['1', '2']:
            exit()
        if _type == '1':

            num = input('需要创建的数量(数字): ')
            try:
                num = int(num)
                if num == 0: raise BaseException('')
            except:
                self.stdout.write(self.style.SUCCESS('无效数字, 请重新运行命令进行操作!'))
                exit()

            days = input('请设置激活码的天数(数字): ')
            try:
                days = int(days)
                if days == 0: raise BaseException('')
            except:
                self.stdout.write(self.style.SUCCESS('无效数字, 请重新运行命令进行操作!'))
                exit()

            for _num in range(num):
                data = {
                    'code': md5(f"{uuid.uuid4()}.{_num}.{time.time()}"),
                    'days': days
                }
                ret = Coupon.objects.create(**data)
                print(f'激活码: {ret.code}  天数: {ret.days}')


        if _type == '2':
            data_list = Coupon.objects.filter(status=1)
            if len(data_list) == 0:
                self.stdout.write(self.style.SUCCESS('目前无未使用激活码'))
                exit()
            for code in data_list:
                print(f'激活码: {code.code}  天数: {code.days}')

        self.stdout.write(self.style.SUCCESS('操作成功'))