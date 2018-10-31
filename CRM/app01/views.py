from django.shortcuts import render, HttpResponse, redirect
from rbac.models import *

# Create your views here.


def login(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        user_obj = User.objects.filter(user=user, pwd=pwd).first()
        if user_obj:
            # 存储登录状态
            request.session['user'] = user_obj.user
            # 查看用户的权限
            permissions = user_obj.roles.all().values('permissions__url', 'permissions__title', 'permissions__code')\
                .distinct()

            # 获取权限url列表
            permission_url_list = []
            permission_menu_list = []
            for permission_dict in permissions:
                permission_url_list.append(permission_dict['permissions__url'])
                if permission_dict['permissions__code'] == 'list':
                    permission_menu_list.append({
                        'title': permission_dict['permissions__title'],
                        'url': permission_dict['permissions__url']
                    })
            print(permission_menu_list)
            request.session['permission_url_list'] = permission_url_list
            request.session['permission_menu_list'] = permission_menu_list
            return redirect('/index/')
    return render(request, 'login.html')


def index(request):
    user = request.session.get('user')
    return render(request, 'index.html', locals())


def no_permission(request):
    return render(request, 'no_permission.html')


def my_logout(request):
    del request.session['user']
    return redirect('/login/')