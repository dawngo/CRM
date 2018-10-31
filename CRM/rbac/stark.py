from rbac.models import *
from stark.service.sites import site, ModelStark


class UserConfig(ModelStark):
    list_display = ['user', 'pwd', 'roles']


class RoleConfig(ModelStark):
    list_display = ['title', 'permissions']


class PermissionConfig(ModelStark):
    list_display = ['url', 'title', 'code']


site.register(User, UserConfig)
site.register(Role, RoleConfig)
site.register(Permission, PermissionConfig)


