from django.conf.urls import url
from django.shortcuts import render, redirect
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django import forms
from stark.utils.page import MyPage
from django.db.models import Q
import copy


class ShowList(object):
    """
    data_list = data_list[page.start:page.end]
    """
    def __init__(self, config_obj, data_list, request):
        self.config_obj = config_obj
        self.data_list = data_list
        self.request = request
        # 分页
        self.pagination = MyPage(self.request.GET.get('page', 1), self.data_list.count(), self.request, per_page_data=10)
        self.new_data_list = self.data_list[self.pagination.start:self.pagination.end]

    # 构建新的actions
    def get_new_actions(self):
        temp = []
        temp.extend(self.config_obj.actions)
        temp.append(self.config_obj.patch_delete)

        new_actions = []
        for action in temp:
            new_actions.append({
                'text': action.desc,
                'name': action.__name__,
            })
        return new_actions

    def get_header(self):
        # 构建表头部分 最终想要的数据类型 header_list = ['书籍名称','价格']
        header_list = []
        for field_or_func in self.config_obj.new_list_display():
            if callable(field_or_func):  # 自定义配置类中函数的处理
                val = field_or_func(self.config_obj, is_header=True)
            else:
                if field_or_func == '__str__':
                    val = self.config_obj.model._meta.model_name.upper()
                else:
                    field_obj = self.config_obj.model._meta.get_field(field_or_func)
                    val = field_obj.verbose_name
            header_list.append(val)
        return header_list

    def get_body(self):
        # 构建表单部分 最终想要的数据类型--> [["python",122],["python",122]]
        new_data_list = []
        for obj in self.new_data_list:
            temp = []
            for field_or_func in self.config_obj.new_list_display():
                if callable(field_or_func):  # 自定义配置类中函数的处理
                    val = field_or_func(self.config_obj, obj=obj)
                else:
                    try:  # 自定义配置类对象的查看展示
                        from django.db.models.fields.related import ManyToManyField
                        field_obj = self.config_obj.model._meta.get_field(field_or_func)

                        if isinstance(field_obj, ManyToManyField):
                            rel_data_list = getattr(obj, field_or_func).all()  # 多对多字段的展示
                            rel_field = [str(item) for item in rel_data_list]
                            val = ', '.join(rel_field)
                        else:
                            val = getattr(obj, field_or_func)  # 通过反射获取对象具体字段的值
                            if field_or_func in self.config_obj.list_display_links:
                                _url = self.config_obj.get_change_url(obj)
                                val = mark_safe("<a href='{}'>{}</a>".format(_url, val))

                    except Exception as e:  # 默认配置类对象的查看展示
                        val = getattr(obj, field_or_func)
                temp.append(val)
            new_data_list.append(temp)
        return new_data_list

    def get_list_filter_links(self):
        # print(self.config_obj.list_filter)  # ['publish', 'authors']
        list_filter_links = {}
        for field in self.config_obj.list_filter:
            params = copy.deepcopy(self.request.GET)
            current_field_pk = params.get(field, 0)  # 获取字段是否带值过来

            field_obj = self.config_obj.model._meta.get_field(field)
            rel_model = field_obj.rel.to  # 获取字段关联的表
            rel_model_queryset = rel_model.objects.all()  # 获取关联表的所有数据
            temp = []
            for obj in rel_model_queryset:
                params[field] = obj.pk
                link = "<a href='?{}' class='list-group-item'>{}</a>".format(params.urlencode(), str(obj))
                if obj.pk == int(current_field_pk):
                    link = "<a href='?{}' class='my_active list-group-item'>{}</a>".format(params.urlencode(), str(obj))
                temp.append(link)
            list_filter_links[field] = temp
        return list_filter_links


class ModelStark(object):
    """
    默认配置类
    """
    list_display = ['__str__']
    model_form_class = []
    list_display_links = []
    search_fields = []
    actions = []
    list_filter = []

    def __init__(self, model):
        self.model = model
        self.model_name = self.model._meta.model_name
        self.app_label = self.model._meta.app_label

    # 批量处理函数
    def patch_delete(self, queryset):
        queryset.delete()

    patch_delete.desc = "删除选中部分"

    # 反向解析当前查看表的url
    def get_list_url(self):
        url_name = '{}_{}_list'.format(self.app_label, self.model_name)
        url = reverse(url_name)
        return url

    def get_add_url(self):
        url_name = '{}_{}_add'.format(self.app_label, self.model_name)
        url = reverse(url_name)
        return url

    def get_change_url(self, obj):
        url_name = '{}_{}_change'.format(self.app_label, self.model_name)
        url = reverse(url_name, args=(obj.pk,))
        return url

    def get_del_url(self, obj):
        url_name = '{}_{}_del'.format(self.app_label, self.model_name)
        url = reverse(url_name, args=(obj.pk,))
        return url

    # 默认操作函数
    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return '选择'
        return mark_safe("<input name='pk' type='checkbox' value={}>".format(obj.pk))

    def edit(self, obj=None, is_header=False):
        if is_header:
            return '操作'
        return mark_safe("<a class='btn btn-info btn-xs' href='{}'>编辑</a>".format(self.get_change_url(obj)))

    def delete(self, obj=None, is_header=False):
        if is_header:
            return '操作'
        return mark_safe("<a class='btn btn-danger btn-xs' href='{}'>删除</a>".format(self.get_del_url(obj)))

    # 构建新的new_list_display
    def new_list_display(self):
        temp = []
        temp.extend(self.list_display)
        temp.insert(0, ModelStark.checkbox)
        if not self.list_display_links:
            temp.append(ModelStark.edit)
        temp.append(ModelStark.delete)
        return temp

    # 获取搜索条件
    def get_search_condition(self, request):
        val = request.GET.get('search_condition')
        search_condition = Q()
        if val:
            search_condition.connector = 'or'
            for field in self.search_fields:
                search_condition.children.append((field + '__icontains', val))
        return search_condition

    def get_filter_condition(self, request):
        filter_condition = Q()
        for key, val in request.GET.items():
            if key in ['page', 'search_condition']:
                continue
            filter_condition.children.append((key, val))
        return filter_condition

    # 视图函数
    def list_view(self, request):
        # print(self)  # 当前访问模型的配置类对象
        # print(self.model)  # 当前访问模型表
        if request.method == 'POST':
            action = request.POST.get('action')
            if action:
                pk_list = request.POST.getlist('pk')
                queryset = self.model.objects.filter(pk__in=pk_list)
                getattr(self, action)(queryset)

        data_list = self.model.objects.all()
        list_url = self.get_list_url()
        add_url = self.get_add_url()

        # 获取查询条件
        search_condition = self.get_search_condition(request)
        if search_condition:
            data_list = self.model.objects.filter(search_condition)

        # 获取过滤条件
        filter_condition = self.get_filter_condition(request)
        if filter_condition:
            data_list = self.model.objects.filter(filter_condition)
        # 分页展示
        show_list = ShowList(self, data_list, request)
        show_list.get_list_filter_links()
        return render(request, 'stark/list_view.html', locals())

    def get_model_form_class(self):
        if self.model_form_class:
            ModelFormClass = self.model_form_class
        else:
            class ModelFormClass(forms.ModelForm):
                class Meta:
                    model = self.model
                    fields = '__all__'
        return ModelFormClass

    def get_new_from(self, form):
        from django.forms.models import ModelChoiceField
        for bfield in form:  # 循环form字段
            if isinstance(bfield.field, ModelChoiceField):
                bfield.is_pop = True
                rel_model = self.model._meta.get_field(bfield.name).rel.to
                model_name = rel_model._meta.model_name
                app_lable = rel_model._meta.app_label
                _url = reverse('{}_{}_add'.format(app_lable, model_name))
                bfield.url = _url
                bfield.pop_back_id = 'id_' + bfield.name
        return form

    def add_view(self, request):
        ModelFormClass = self.get_model_form_class()

        if request.method == 'POST':
            form = ModelFormClass(request.POST)
            form = self.get_new_from(form)
            if form.is_valid():
                obj = form.save()
                is_pop = request.GET.get('pop')
                if is_pop:
                    text = str(obj)
                    pk = obj.pk
                    return render(request, 'stark/pop.html', locals())
                return redirect(self.get_list_url())
            return render(request, 'stark/add_view.html', locals())
        form = ModelFormClass()
        form = self.get_new_from(form)
        return render(request, 'stark/add_view.html', locals())

    def change_view(self, request, id):
        ModelFormClass = self.get_model_form_class()
        edit_obj = self.model.objects.get(pk=id)

        if request.method == 'POST':
            form = ModelFormClass(data=request.POST, instance=edit_obj)
            form = self.get_new_from(form)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, 'stark/change_view.html', locals())
        form = ModelFormClass(instance=edit_obj)
        form = self.get_new_from(form)
        return render(request, 'stark/change_view.html', locals())

    def del_view(self, request, id):
        del_obj = self.model.objects.get(pk=id)

        # 构建表头部分 最终想要的数据类型 header_list = ['书籍名称','价格']
        header_list = []
        for field_or_func in self.list_display:
            if callable(field_or_func):
                val = field_or_func(self, is_header=True)
            else:
                if field_or_func == '__str__':
                    val = self.model._meta.model_name.upper()
                else:
                    field_obj = self.model._meta.get_field(field_or_func)
                    val = field_obj.verbose_name
            header_list.append(val)

        # 构建表单部分 最终想要的数据类型--> ["python",122]
        del_obj_temp = []
        for field_or_func in self.list_display:
            if callable(field_or_func):
                val = field_or_func(self, del_obj)
            else:
                if field_or_func == '__str__':
                    val = getattr(del_obj, field_or_func)
                else:
                    from django.db.models.fields.related import ManyToManyField
                    field_obj = self.model._meta.get_field(field_or_func)
                    if isinstance(field_obj, ManyToManyField):
                        rel_data_list = getattr(del_obj, field_or_func).all()  # 多对多字段的展示
                        rel_field = [str(item) for item in rel_data_list]
                        val = ', '.join(rel_field)
                    else:
                        val = getattr(del_obj, field_or_func)  # 通过反射获取对象具体字段的值

            del_obj_temp.append(val)

        list_url = self.get_list_url()
        if request.method == 'POST':
            del_obj.delete()
            return redirect(list_url)

        return render(request, 'stark/del_sure.html', locals())

    # 二级url的获取
    def extra_url(self):
        return []

    def get_urls(self):
        temp = [
            url(r'^$', self.list_view, name='{}_{}_list'.format(self.app_label, self.model_name)),
            url(r'add/$', self.add_view, name='{}_{}_add'.format(self.app_label, self.model_name)),
            url(r'(\d+)/change/$', self.change_view, name='{}_{}_change'.format(self.app_label, self.model_name)),
            url(r'(\d+)/delete/$', self.del_view, name='{}_{}_del'.format(self.app_label, self.model_name)),
        ]
        temp.extend(self.extra_url())
        return temp

    @property
    def urls(self):
        return self.get_urls(), None, None


class AdminSite(object):
    """
    stark的全局组件
    """
    def __init__(self):
        self._registry = {}

    def register(self, model, admin_class=None):
        # 设置配置类
        if not admin_class:
            admin_class = ModelStark

        self._registry[model] = admin_class(model)

    def get_urls(self):
        temp = []

        for model, config_obj in self._registry.items():
            model_name = model._meta.model_name
            app_label = model._meta.app_label
            temp.append(url(r'{}/{}/'.format(app_label, model_name), config_obj.urls))
        return temp

    @property
    def urls(self):
        return self.get_urls(), None, None


site = AdminSite()
