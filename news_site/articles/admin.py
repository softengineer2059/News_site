from django.contrib import admin
from .models import *




class Article_admin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'category', 'subcategory', 'created_at', 'updated_at', 'is_published']
    list_display_links = ['title']
    search_fields = ['title', 'slug', 'author', 'category', 'subcategory', 'created_at', 'updated_at', 'is_published', 'tags']


class Category_admin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_display_links = ['name']
    search_fields = ['name']


class Subcategory_admin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category_name']
    list_display_links = ['name']
    search_fields = ['name']


class ArticleImage_admin(admin.ModelAdmin):
    list_display = ['article', 'image', 'caption']
    list_display_links = ['article']
    search_fields = ['article']


class Tags_admin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_display_links = ['name', 'slug']
    search_fields = ['name', 'slug']


class Country_admin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_display_links = ['name', 'slug']
    search_fields = ['name', 'slug']


admin.site.register(Article, Article_admin)
admin.site.register(Category, Category_admin)
admin.site.register(ArticleImage, ArticleImage_admin)
admin.site.register(Tag, Tags_admin)
admin.site.register(Subcategory, Subcategory_admin)
admin.site.register(Country, Country_admin)