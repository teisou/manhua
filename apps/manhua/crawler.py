import os, datetime, time, threading, queue
from multiprocessing import Process, cpu_count

from urllib.parse import urlparse
import requests
from apps.manhua import models

from conf import config

from libs.database import RedisClient


# 进程数量
MAX_PROCESSES = cpu_count() // 2 or cpu_count()

# 线程数量
MAX_THREADING = cpu_count() * 2 or cpu_count()

class XieMan():
    def __init__(self):
        self.curl = requests.session()
        self.curl.timeout = 30
        self.curl.headers = {
            'access-token': config.UPDATE_TOKEN
        }
        self.base_url = 'https://www.xieman.cc'

    # 获取漫画列表 源站
    def get_books_meto(self):
        url = 'https://www.meto3517.com/query/books?paged=true&size=500&page=1&orderBy=newest&type=cartoon'
        ret = self.curl.get(url)
        return ret.json()['content']['list']

    # 获取漫画列表
    def get_books(self):
        url = f'{self.base_url}/api/get/books'
        if not self.report_get(url): return False
        return True
        # print(self.ret)

    # 获取章节列表
    def get_directory(self, book_id):
        url = f'{self.base_url}/api/get/directory/{book_id}'
        if not self.report_get(url): return False
        return True

    # get_chapter_images
    def get_chapter_images(self, chapter_id):
        url = f'{self.base_url}/api/get/chapter/{chapter_id}'
        if not self.report_get(url): return False
        return True

    # 统计 get 请求
    def report_get(self, url):
        try:
            ret = self.curl.get(url)
            # print(ret.text)
            self.ret = ret.json()
            if ret.status_code == 200:
                return True
            return False
        except BaseException as e:
            print(e)
            return False

    # 下载图片
    def download_image(self, url):
        try:
            print(f'正在下载 {url}')

            # 获取文件名
            filename = os.path.basename(url)

            # 获取图片本地存放目录
            pathdir = config.IMAGES_PATH + urlparse(url).path.replace(filename, '')

            # 获取图片路径
            self.filename = urlparse(url).path
            try:
                if not os.path.exists(pathdir): os.makedirs(pathdir)
            except: pass


            image_filename = os.path.join(pathdir, os.path.basename(url))

            # 如果图片已经存在则不再进行下载
            if os.path.exists(image_filename): return True



            # 下载并保存图片
            resq = self.curl.get(url, timeout=30)
            if resq.status_code != 200: raise BaseException(resq.status_code)
            with open(image_filename, 'wb') as f:
                f.write(resq.content)

            return True

        except BaseException as e:
            print(f'下载失败 {url} {e}')
            return False


def print_log(message):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + f'    {message}')

# 更新漫画列表
def update_books():
    xApi = XieMan()
    if not xApi.get_books(): return False, '获取漫画列表失败'

    # 更新分类列表
    for cate in xApi.ret['category']:
        _id = cate['id']
        _name = cate['name']
        models.Category.objects.filter(id=_id).get_or_create(id=_id, name=_name)

    # 遍历漫画列表
    for book in xApi.ret['data']:
        data = {
            'id': book['id'],
            'name': book['name'],
            'author': book['author'],
            'description': book['description'],
            'keywords': book['keywords'],
            'category_id': book['category_id'],
            'status': book['status'],
            'free_flag': book['free_flag'],  # 是否免费
            'onsale': book['onsale'],
            'cover_url': book['cover_url'],
            'square_image': book['square_image'],
            'extension_url': book['extension_url'],
            'tags': book['tags'],
            'recommend': book['recommend'],
            # 'competitive': book['competitive'],
            'score': book['score'],
            'update_day': book['update_day'],  # 更新时间
            'h': book['h'],
            'fresh': book.get('fresh', False),
            'vip_free': book['vip_free'],   # vip 是否免费
            'exclusive': book['exclusive'],
            'read_count': book['read_count'],
            'like_count': book['like_count'],
        }
        book_info = models.Books.objects.filter(id=data['id']).first()
        if book_info:
            # 如果漫画存在
            if book_info.cover_url.startswith('/'):
                del data['cover_url']

            if book_info.square_image.startswith('/'):
                del data['square_image']

            if book_info.extension_url.startswith('/'):
                del data['extension_url']


            models.Books.objects.filter(id=data['id']).update(**data)
        else:
            book_info = models.Books.objects.create(**data)
        book_update_chapter(book_info.id)
        book_update_images(book_info.id)

    # models.Books.objects.filter()


# 更新下载漫画封面图片
def book_update_images(book_id):
    book_info = models.Books.objects.filter(id=book_id).first()
    if not book_info: return False

    # 判断是否设置了 图片目录
    if config.IMAGES_PATH == '': return False

    print(f'正在更新 封面图片 {book_info.name}({book_info.id})')
    mhApi = XieMan()
    if not book_info.cover_url.startswith('/'):
        if mhApi.download_image(book_info.cover_url): book_info.cover_url = mhApi.filename

    if not book_info.square_image.startswith('/'):
        if mhApi.download_image(book_info.square_image): book_info.square_image = mhApi.filename

    if not book_info.extension_url.startswith('/'):
        if mhApi.download_image(book_info.extension_url): book_info.extension_url = mhApi.filename
    book_info.save()
    return True


# 更新漫画章节
def book_update_chapter(book_id):
    book_info = models.Books.objects.filter(id=book_id).first()
    if not book_info: return False, '漫画不存在'
    xApi = XieMan()
    if not xApi.get_directory(book_id): return False, '获取章节列表失败'

    for chapter in xApi.ret['data']:
        data = {
            'id': chapter['id'],
            'title': chapter['title'],
            'books_id': chapter['books_id'],
            'sequence': chapter['sequence'],
            'cover_url': chapter['cover_url'],
            'free_flag': chapter['free_flag'],
            'points': chapter['points'],
            'has_read': chapter['has_read'],
            'has_purchase': chapter['has_purchase'],
            'vip_free': chapter['vip_free'],
        }
        if models.Chapter.objects.filter(id=data['id']).first():
            models.Chapter.objects.filter(id=data['id']).update(**data)
        else:
            data.update({
                'display': False
            })
            models.Chapter.objects.create(**data)
        continue
    print_log(f'{book_info.name} ({book_info.id}) 更新完成')
    return True

# 更新全部章节图片 (排除已更新)
def start_chapter_update_images():
    ids = models.Chapter.objects.filter(display=False).order_by('id').values_list('id', flat=True)

    print_log(f"共有 {len(ids)} 章节需要进行更新")
    time.sleep(5)
    threads = []
    _queue = queue.Queue()
    lock = threading.Lock()

    # 线程并发下载， 如果 服务器配置好, 可以适当调大, 不建议超过 200
    num = threading.Semaphore(MAX_THREADING)

    for _id in ids:
        t = DownThread(_queue, lock, num, 'chapter')
        threads.append(t)
        _queue.put(_id)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    _queue.join()


# 更新章节信息
def chapter_update_images(chapter_id):
    # 判断章节是否存在且未进行更新
    chapter_info = models.Chapter.objects.filter(id=chapter_id, display=False).first()
    if not chapter_info: return False, '章节不存在'

    print_log(f'正在更新 {chapter_info.books.name}({chapter_info.books.id}) {chapter_info.title}({chapter_info.id})')

    xApi = XieMan()
    if not xApi.get_chapter_images(chapter_id): return False, '获取图片列表失败'
    for image in xApi.ret['data']:
        data = {
            'id': image['id'],
            'chapter_id': image['chapter_id'],
            'url': image['url'],
            'sequence': image['sequence'],
            'width': image['width'],
            'height': image['height'],
        }
        if models.Images.objects.filter(id=data['id']).first():
            models.Images.objects.filter(id=data['id']).update(**data)
        else:
            models.Images.objects.filter(id=data['id']).create(**data)
        continue
    chapter_info.display = 1
    chapter_info.save()
    print_log(f'更新完成 {chapter_info.books.name}({chapter_info.books.id}) {chapter_info.title}({chapter_info.id})')
    return True

# 更新漫画列表 源站
def update_books_meto():
    xApi = XieMan()
    ret = xApi.get_books_meto()
    for book in ret:
        data = {
            'extension_url': book['extensionUrl'],
            'square_image': book['squareImage'],
            'cover_url': book['coverUrl'],
        }
        book_id = book['id']
        models.Books.objects.filter(id=book_id).update(**data)

# 下载单个图片文件
def one_download_images(image_id):
    mhApi = XieMan()
    image = models.Images.objects.filter(url__startswith='http', id=image_id).first()
    if not image: return False
    if not mhApi.download_image(image.url): return False
    image.url = mhApi.filename
    image.save()
    return True


# 下载全部章节外链图片
def download_chapter_images():
    if config.IMAGES_PATH == '':
        print_log(f"未配置图片下载目录，无需进行下载")
        return False

    # 每次最多下载 3 W 张
    images = models.Images.objects.filter(url__startswith='http').order_by('-id')[:30000]
    print_log(f"共有 {len(images)} 张图片需要进行下载")
    time.sleep(5)

    # xmApi = XieMan()

    threads = []
    _queue = queue.Queue()
    lock = threading.Lock()

    # 10个线程并发下载， 如果 服务器配置好, 可以适当调大, 不建议超过 200
    num = threading.Semaphore(MAX_THREADING)


    for image in images:
        t = DownThread(_queue, lock, num, 'images')
        threads.append(t)
        _queue.put(image.id)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    _queue.join()


# 下载线程
class DownThread(threading.Thread):
    def __init__(self, queue, lock, num, _type):
        super(DownThread, self).__init__()
        self.queue = queue
        self.num = num
        self.lock = lock
        self._type = _type

    def run(self):
        with self.num:
            try:
                data_id = self.queue.get()

                # 下载图片
                if self._type == 'images':
                    one_download_images(data_id)

                # 更新章节
                if self._type == 'chapter':
                    chapter_update_images(data_id)
            except Exception as e:
                pass
            # 任务跑完移除线程
            self.queue.task_done()




if __name__ == '__main__':
    update_books()