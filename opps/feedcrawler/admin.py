# coding: utf-8
from django.contrib import admin
from .models import Group, Feed, Entry, FeedConfig
from opps.core.admin import PublishableAdmin
from opps.core.admin import apply_opps_rules


@apply_opps_rules('feedcrawler')
class GroupAdmin(admin.ModelAdmin):
    pass


@apply_opps_rules('feedcrawler')
class FeedAdmin(PublishableAdmin):
    list_display = ['xml_url', 'title', 'slug', 'channel', 'group',
                    'published_time', 'last_polled_time']
    list_filter = ['group', 'channel']
    search_fields = ['link', 'title', 'slug']
    readonly_fields = ['title', 'link', 'description', 'published_time',
                       'last_polled_time']
    raw_id_fields = ('channel', 'main_image')
    fieldsets = (
        (None, {
            'fields': (('site',),
                       ('xml_url', 'group',),
                       ('slug',),
                       ('title', 'link',),
                       ('description',),
                       ('published_time', 'last_polled_time',),
                       ('channel',),
                       ('main_image',)
                       )
        }),
    )


@apply_opps_rules('feedcrawler')
class EntryAdmin(PublishableAdmin):
    list_display = ['entry_title', 'entry_feed', 'entry_published_time']
    list_filter = ['entry_feed']
    search_fields = ['entry_title', 'entry_link']
    readonly_fields = ['entry_link', 'entry_title', 'entry_description',
                       'entry_published_time', 'entry_feed', 'entry_content']
    raw_id_fields = ('channel',)
    fieldsets = (
        (None, {
            'fields': (('site',),
                       ('title',),
                       ('hat',),
                       ('short_title',),
                       ('slug',),
                       ('headline',),
                       ('channel',),
                       ('entry_link',),
                       ('entry_title', 'entry_feed',),
                       ('entry_description',),
                       ('entry_content',),
                       ('entry_published_time',),
                       'entry_source',
                       'published',
                       'date_available',
                       'show_on_root_channel'
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
