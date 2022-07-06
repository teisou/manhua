from django.core.management.base import BaseCommand
from apps.manhua.crawler import start_chapter_update_images

class Command(BaseCommand):
    help = '更新章节列表'

    def handle(self, *args, **options):
        start_chapter_update_images()
        self.stdout.write(self.style.SUCCESS('  章节列表更新完成'))