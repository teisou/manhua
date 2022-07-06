# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <spug.dev@gmail.com>
# Released under the AGPL-3.0 License.
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache
from django.db.models import Q
from apps.users.models import Account

class HandleExceptionMiddleware(MiddlewareMixin):
    """
    处理试图函数异常
    """

    def process_exception(self, request, exception):
        # traceback.print_exc()
        # return json_response(error='Exception: %s' % exception)
        pass

class AuthenticationMiddleware(MiddlewareMixin):
    """
    会话处理
    """

    def process_request(self, request):

        # 获取ip地址
        request.ip = get_ip(request)
        # 获取用户密码
        request.password = request.session.get('password', '')
        # 如果已经登录
        if request.session.get('is_login'):

            # print(request.session.get('user_data'))
            request.user = request.session.get('user_data')
            request.user_info = Account.objects.filter(id=request.user.get('id')).first()
            # print(request.user_info)
            request.is_login = request.session.get('is_login')
        else:
            request.is_login = False
            request.user_info = object

        return None



# 获取IP地址
def get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
        ip = ip.split(',')[0]
    else:
        ip = request.META['REMOTE_ADDR']
    return ip