#coding=utf-8
from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from models import Event, Category
from django.conf import settings

from facebook.admin import AdminBase
from facebook.utils import get_graph, get_public_graph, get_static_graph

""" Add fh-admin Facebook app to your server secrets.py if the admin frontend is hosted on Lemur.

    'fh-admin' : {
        'ID': '230650940299284',
        'API-KEY': '',
        'SECRET': 'da928133383970e1159546c99cb8d464',
        'CANVAS-PAGE': 'https://apps.facebook.com/fh-admin/',
        'CANVAS-URL': 'http://feinheit.ch',
        'SECURE-CANVAS-URL': 'https://feinheit.ch',
        'REDIRECT-URL': 'http://apps.facebook.com/fh-admin/',
    }
"""


class EventAdmin(AdminBase):

    def save_model(self, request, obj, form, change):
        graph = get_graph(request, app_name='fh-admin')
        obj.get_from_facebook(graph=graph, save=True)


    list_display=('profile_link', 'id', '_name', '_start_time', '_end_time', '_location' )
    list_display_links = ('id',)
    readonly_fields = ('_graph', '_owner', '_name', '_description', 
                       '_start_time', '_end_time', '_location', '_venue', 
                       '_privacy', '_updated_time', 'image')
    list_filter = ('_start_time', 'categories')

    fieldsets = [
        (None, {
            'fields': ('id', 'language', 'categories', 
                       ('max_places', '_privacy'),
                       ('_name', 'slug'), '_description',
                       ('_start_time', '_end_time'),
                       ('_location', '_venue'),
                       '_owner', 'image', '_graph', 'access_token')
                })]
    prepopulated_fields = {'slug' : ('id',)}

admin.site.register(Event, EventAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display=('name', 'slug')
    prepopulated_fields = {'slug' : ('name',)}
    
admin.site.register(Category, CategoryAdmin)