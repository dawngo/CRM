from django.shortcuts import render, redirect, HttpResponse
from django.utils.deprecation import MiddlewareMixin
import re


class PermissionMiddleware(MiddlewareMixin):

    def process_request(self, request):
        current_path = request.path

        # 白名单
        white_url = ['/login/', '/index/', '/admin/.*', '/no_permission/', '/logout/']
        for reg in white_url:
            ret = re.search(reg, current_path)
            if ret:
                return None

        # 校验用户是否登录
        user = request.session.get('user')
        if not user:
            return redirect('/login/')

        # 校验用户是否有权限访问
        permission_url_list = request.session.get('permission_url_list')
        for permission_url in permission_url_list:
            permission_url = "^%s$" % permission_url
            obj = re.search(permission_url, current_path)
            if obj:
                return None
        return redirect('/no_permission/')


