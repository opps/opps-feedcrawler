# coding: utf-8
from django.contrib import admin
from .models import Group, Feed, Entry, FeedConfig
from opps.core.admin import PublishableAdmin


class GroupAdmin(admin.ModelAdmin):
    pass


class FeedAdmin(PublishableAdmin):
    list_display = ['xml_url', 'title', 'group',
                    'published_time', 'last_polled_time']
    list_filter = ['group']
    search_fields = ['link', 'title']
    readonly_fields = ['title', 'link', 'description', 'published_time',
                       'last_polled_time']
    fieldsets = (
        (None, {
            'fields': (('xml_url', 'group',),
                       ('title', 'link',),
                       ('description',),
                       ('published_time', 'last_polled_time',),
                       )
        }),
    )


class EntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'feed', 'published_time']
    list_filter = ['feed']
    search_fields = ['title', 'link']
    readonly_fields = ['link', 'title', 'description',
                       'published_time', 'feed', 'content']
    fieldsets = (
        (None, {
            'fields': (('link',),
                       ('title', 'feed',),
                       ('description',),
                       ('content',),
                       ('published_time',),
                       'entry_source'
                       )
        }),
    )


class FeedConfigAdmin(PublishableAdmin):
    list_display = ['key', 'key_group', 'channel', 'date_insert',
                    'date_available', 'published']
    list_filter = ["key", 'key_group', "channel", "published"]
    search_fields = ["key", "key_group", "value"]
    raw_id_fields = ['feed', 'channel', 'article']
    exclude = ('user',)

admin.site.register(Feed, FeedAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(FeedConfig, FeedConfigAdmin)
