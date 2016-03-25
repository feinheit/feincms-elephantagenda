# coding=utf-8
from django.contrib import admin

from models import Event, Category

from facebook.admin import AdminBase
from facebook.utils import get_graph, get_public_graph, get_static_graph


class EventAdmin(AdminBase):

    def save_model(self, request, obj, form, change):
        graph = get_graph(request, app_name='fh-admin')
        obj.get_from_facebook(graph=graph, save=True)

    list_display = ('profile_link', 'id', '_name',
                    '_start_time', '_end_time', '_location')
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
    prepopulated_fields = {'slug': ('id',)}

admin.site.register(Event, EventAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)
