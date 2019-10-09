#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "David"
# Date: 2018/9/4
"""
from stark.service.sites import site, ModelStark
from app01.models import *
from django import forms
# print('app01...')


class BookModelForm(forms.ModelForm):
    class Meta:
        val = {'required': '该字段不能为空！'}
        model = Book
        fields = '__all__'
        widgets = {
            "publishDate": forms.widgets.DateInput(
                attrs={"type": "date", "class": "form-control"}
            )
        }
        error_messages = {
            'title': val,
            'price': val,
        }


class BookConfig(ModelStark):
    list_display = ['title', 'price', 'publish', 'authors']
    model_form_class = BookModelForm
    list_display_links = ['title', 'price']
    search_fields = ['title', 'price']

    def patch_init(self, queryset):
        queryset.update(price=99)

    patch_init.desc = "价格初始化"

    actions = [patch_init]

    list_filter = ['publish', 'authors']


class AuthorDetailModelForm(forms.ModelForm):
    class Meta:
        model = AuthorDetail
        fields = '__all__'
        widgets = {
            "birthday": forms.widgets.DateInput(
                attrs={"type": "date", "class": "form-control"}
            )
        }


class AuthorDetailConfig(ModelStark):
    model_form_class = AuthorDetailModelForm


site.register(Book, BookConfig)
site.register(Publish)
site.register(Author)
site.register(AuthorDetail, AuthorDetailConfig)


# print(site._registry)
"""
