from django.core.management.base import BaseCommand
from apps.manhua.crawler import download_chapter_images

class Command(BaseCommand):
    help = '更新章节图片列表'

    def handle(self, *args, **options):
        download_chapter_images()
        self.stdout.write(self.style.SUCCESS('  图片列表更新成功'))