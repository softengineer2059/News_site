from django.contrib import admin
from .models import *


class Comments_admin(admin.ModelAdmin):
    list_display = ['article', 'user', 'text', 'created_at', 'parent']
    list_display_links = ['article', 'user', 'text', 'created_at', 'parent']
    search_fields = ['article', 'user', 'text', 'created_at', 'parent']


admin.site.register(Comments, Comments_admin)