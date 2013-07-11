# coding: utf-8
from django.contrib import admin
from .models import Group, Feed, Entry, FeedType
from opps.core.admin import PublishableAdmin
from opps.core.admin import apply_opps_rules


@apply_opps_rules('feedcrawler')
class FeedTypeAdmin(admin.ModelAdmin):
    pass


@apply_opps_rules('feedcrawler')
class GroupAdmin(admin.ModelAdmin):
    pass


@apply_opps_rules('feedcrawler')
class FeedAdmin(PublishableAdmin):
    list_display = ['title', 'slug', 'source_url', 'feed_type', 'channel', 'group',
                    'published_time', 'last_polled_time']
    list_filter = ['group', 'channel', 'feed_type']
    search_fields = ['link', 'title', 'slug', 'description']
    readonly_fields = ['published_time',
                       'last_polled_time']
    raw_id_fields = ('channel', 'main_image')
    fieldsets = (
        (None, {
            'fields': (('site',),
                       ('title',),
                       ('slug',),
                       ('group',),
                       ('feed_type',),
                       ('link',),
                       ('description',),
                       ('published_time', 'last_polled_time',),
                       ('channel',),
                       ('main_image',),
                       ('max_entries',),

                       ('source_url',),
                       ('source_username',),
                       ('source_password',),
                       ('source_port',),
                       ('source_root_folder',),
                       ('source_json_params',),
                       )
        }),
    )


@apply_opps_rules('feedcrawler')
class EntryAdmin(PublishableAdmin):
    list_display = ['entry_title', 'entry_feed', 'entry_published_time']
    list_filter = ['entry_feed']
    search_fields = ['entry_title', 'entry_link', 'entry_description']
    readonly_fields = ['entry_link', 'entry_title', 'entry_description',
                       'entry_published_time', 'entry_feed', 'entry_content',
                       'entry_pulled_time']
    raw_id_fields = ('channel',)
    fieldsets = (
        (None, {
            'fields': (('site',),
                       ('title',),
                       ('hat',),
                       ('slug',),
                       ('channel',),
                       ('entry_link',),
                       ('entry_title', 'entry_feed',),
                       ('entry_description',),
                       ('entry_content',),
                       ('entry_published_time',),
                       ('entry_pulled_time',),
                       'entry_json',
                       'published',
                       'date_available',
                       'show_on_root_channel'
                       )
        }),
    )

admin.site.register(Feed, FeedAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(FeedType, FeedTypeAdmin)
