#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from random import getrandbits
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone

from opps.core.models import Publishable, Slugged
from opps.containers.models import Container
from opps.channels.models import Channel

RSS_PROCESSOR = 'opps.feedcrawler.processors.rss.RSSProcessor'
RSS_ACTIONS = 'opps.feedcrawler.actions.rss.RSSActions'


class FeedType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    processor = models.CharField(max_length=255, default=RSS_PROCESSOR)
    actions = models.CharField(max_length=255, default=RSS_ACTIONS)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'Feed Type')
        verbose_name_plural = _(u'Feed Types')


class Group(models.Model):
    name = models.CharField(max_length=250, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = _(u'Group')
        verbose_name_plural = _(u'Groups')

    def __unicode__(self):
        return self.name

    def num_unread(self):
        return len(Entry.objects.filter(feed__group=self, read=False))


class Feed(Publishable, Slugged):
    title = models.CharField(max_length=255)

    description = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=2000, blank=True, null=True)

    source_url = models.CharField(max_length=255)

    source_username = models.CharField(max_length=255, blank=True, null=True)
    source_password = models.CharField(max_length=255, blank=True, null=True)
    source_port = models.PositiveIntegerField(blank=True, null=True)
    source_root_folder = models.CharField(max_length=255, default="/")

    source_json_params = models.TextField(blank=True, null=True)

    published_time = models.DateTimeField(blank=True, null=True)
    last_polled_time = models.DateTimeField(blank=True, null=True)

    group = models.ForeignKey(Group, blank=True, null=True,
                              verbose_name=_(u"Group or Source"))
    feed_type = models.ForeignKey(FeedType)

    max_entries = models.PositiveIntegerField(blank=True, null=True)

    publish_entries = models.BooleanField(default=True)

    channel = models.ForeignKey(
        'channels.Channel',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    main_image = models.ForeignKey(
        'images.Image',
        verbose_name=_(u'Feed Image'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='feed_image'
    )

    class Meta:
        ordering = ['title']
        verbose_name = _(u'Feed')
        verbose_name_plural = _(u'Feeds')

    def __unicode__(self):
        return self.title

    def load_json_params(self):
        if self.source_json_params:
            try:
                return json.loads(self.source_json_params or "{}")
            except:
                raise ValidationError(_(u'Invalid JSON'))

    def clean(self):
        self.load_json_params()

    @property
    def entries(self):
        return self.entry_set.all()

    # def get_absolute_url(self):
    #     return "/feed/{0}/{1}".format(self.channel.long_slug, self.slug)

    def get_http_absolute_url(self):
        protocol, path = "http://{0}/{1}".format(
            self.channel, self.slug).split(self.site.domain)
        return "{0}{1}/feed{2}".format(protocol, self.site, path)

    def get_processor(self, verbose=False):
        try:
            processor = self.feed_type.processor
            _module = '.'.join(processor.split('.')[:-1])
            _processor = processor.split('.')[-1]
            _temp = __import__(_module, globals(), locals(), [_processor], -1)
            Processor = getattr(_temp, _processor)
            return Processor(self, verbose=verbose)
        except Exception as e:
            print str(e)
            return

    def create_channel(self):
        try:
            channel = Channel.objects.get(slug=self.slug)
        except:
            channel = Channel.objects.create(
                name=self.title,
                slug=self.slug,
                published=True,
                site=self.site,
                user=self.user
            )
        self.channel = channel
        self.save()
        return channel

    def get_channel(self):
        return (self.channel or
                Channel.objects.get_homepage(site=self.site) or
                self.create_channel())


    def save(self, *args, **kwargs):
        exclude = {}
        filters = dict(slug=self.slug)
        if self.pk is not None:
            exclude = dict(pk=self.pk)
        if Feed.objects.filter(**filters).exclude(**exclude).exists():
            # print("exists creating a new slug")
            self.slug = u'{random}-{o.slug}'.format(
                o=self, random=getrandbits(16)
            )
        super(Feed, self).save(*args, **kwargs)



class Entry(Container):
    entry_feed = models.ForeignKey(Feed)
    entry_title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    entry_link = models.CharField(max_length=2000, blank=True, null=True)
    entry_description = models.TextField(blank=True, null=True)
    entry_content = models.TextField(blank=True, null=True)
    entry_published_time = models.DateTimeField(auto_now_add=True)
    entry_pulled_time = models.DateTimeField(auto_now_add=True)
    entry_json = models.TextField(blank=True, null=True)

    entry_category = models.CharField(max_length=255, blank=True, null=True)
    entry_category_code = models.CharField(max_length=255, blank=True,
                                           null=True)

    post_created = models.BooleanField(_(u"Post created"), default=False)

    class Meta:
        ordering = ['-entry_published_time']
        verbose_name = _(u'Entry')
        verbose_name_plural = _(u'Entries')

    def __unicode__(self):
        return self.title

    def get(self, key):
        data = self.load_json()
        return data.get(key)

    def load_json(self):
        try:
            return json.loads(self.entry_json or "{}")
        except:
            raise ValidationError(u"Invalid Json")


class ProcessLog(models.Model):
    feed = models.ForeignKey(Feed)
    type = models.CharField(max_length=255, blank=True, null=True)
    text = models.CharField(max_length=255, blank=True, null=True)
    log_time = models.DateTimeField(auto_now_add=True, default=timezone.now)

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name = _(u'Process Log')
        verbose_name_plural = _(u'Process Logs')
