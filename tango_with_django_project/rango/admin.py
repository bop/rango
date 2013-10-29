from django.contrib import admin
#-*- coding: utf-8  -*-
from .models import Category, Page

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')
    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'views', 'likes')
    verbose_name = 'catégorie'
    verbose_name_plural = 'catégories'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
