# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Group, Feed, Entry, FeedType, ProcessLog
from opps.core.admin import PublishableAdmin
from opps.core.admin import apply_opps_rules


@apply_opps_rules('feedcrawler')
class ProcessLogadmin(admin.ModelAdmin):
    pass


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
                       ('publish_entries',),
                       ('published',),

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

    def has_add_permission(self, request):
        return False

    action_buttons = [
        {"text": _(u"Create post"),
         "url": '/feedcrawler/createpost/{obj.pk}',
         "class": "btn btn-success",
         "style": "",
         "title": _(u"Click to generate a post from this entry")},
    ]

    list_display = ['entry_title', 'entry_feed', 'entry_published_time',
                    'entry_pulled_time', 'entry_category',
                    'entry_category_code', 'published', 'post_created']
    list_filter = ['entry_feed', 'entry_category']
    search_fields = ['entry_title', 'entry_link', 'entry_description']
    readonly_fields = ['entry_link', 'entry_title', 'entry_description',
                       'entry_published_time', 'entry_feed', 'entry_content',
                       'entry_pulled_time', 'entry_category',
                       'entry_category_code', 'content_as_html', 'description_as_html']
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
                       ('entry_category', 'entry_category_code',),
                       ('description_as_html',),
                       ('content_as_html',),
                       ('entry_published_time',),
                       ('entry_pulled_time',),
                       'entry_json',
                       'published',
                       'date_available',
                       'show_on_root_channel'
                       )
        }),
    )


    def content_as_html(self, obj, *args, **kwargs):
        return obj.entry_content
    content_as_html.allow_tags = True
    content_as_html.description = _(u"Content")

    def description_as_html(self, obj, *args, **kwargs):
        return obj.entry_description
    description_as_html.allow_tags = True
    description_as_html.description = _(u"Content")

admin.site.register(Feed, FeedAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(FeedType, FeedTypeAdmin)
admin.site.register(ProcessLog, ProcessLogadmin)
