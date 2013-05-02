#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from opps.core.models import Publishable, BaseConfig, Slugged
from opps.articles.models import Article


class Group(models.Model):
    """
    Group of feeds.

    :Fields:

        name : char
            Name of group.
    """
    name = models.CharField(max_length=250, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def num_unread(self):
        return len(Entry.objects.filter(feed__group=self, read=False))


class Feed(Publishable, Slugged):
    """
    Feed information.

    :Fields:

        title : char
            Title of feed.
        xml_url : char
            URL of xml feed.
        link : char
            URL of feed site.
        description : text
            Description of feed.
        updated_time : date_time
            When feed was last updated.
        last_polled_time : date_time
            When feed was last polled.
        group : ForeignKey
            Group this feed is a part of.
    """
    title = models.CharField(max_length=2000, blank=True, null=True)
    xml_url = models.CharField(max_length=255, unique=True)
    link = models.CharField(max_length=2000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    published_time = models.DateTimeField(blank=True, null=True)
    last_polled_time = models.DateTimeField(blank=True, null=True)
    group = models.ForeignKey(Group, blank=True, null=True)

    channel = models.ForeignKey(
        'channels.Channel',
        null=True,
        blank=False,
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

    def __unicode__(self):
        return self.title

    @property
    def entries(self):
        return self.entry_set.all()

    def save(self, *args, **kwargs):
        """Poll new Feed"""
        try:
            Feed.objects.get(xml_url=self.xml_url)
            super(Feed, self).save(*args, **kwargs)
        except Feed.DoesNotExist:
            super(Feed, self).save(*args, **kwargs)
            from .utils import refresh_feed
            refresh_feed(self)

    def get_absolute_url(self):
        return "/feed/{0}/{1}".format(self.channel.long_slug, self.slug)

    def get_http_absolute_url(self):
        protocol, path = "http://{0}/{1}".format(
            self.channel, self.slug).split(self.site.domain)
        return "{0}{1}/feed{2}".format(protocol, self.site, path)


class Entry(Article):
    """
    Feed entry information.

    :Fields:

        feed : ForeignKey
            Feed this entry is a part of.
        title : char
            Title of entry.
        link : char
            URL of entry.
        description : text
            Description of entry.
        updated_time : date_time
            When entry was last updated.
    """
    entry_feed = models.ForeignKey(Feed)
    entry_title = models.CharField(
        max_length=2000,
        blank=True,
        null=True
    )
    entry_link = models.CharField(max_length=2000)
    entry_description = models.TextField(blank=True, null=True)
    entry_content = models.TextField(blank=True, null=True)
    entry_published_time = models.DateTimeField(auto_now_add=True)
    entry_source = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-entry_published_time']
        verbose_name_plural = 'entries'

    def __unicode__(self):
        return self.title

    # def get_absolute_url(self):
    #     return self.entry_link

    # def get_http_absolute_url(self):
    #     return self.entry_link
    # get_http_absolute_url.short_description = 'URL'


class FeedConfig(BaseConfig):
    """
    max_entries_saved
    """

    feed = models.ForeignKey(
        'feedcrawler.Feed',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='feedconfig_feeds',
        verbose_name=_(u'Feed'),
    )

    class Meta:
        permissions = (("developer", "Developer"),)
        unique_together = ("key_group", "key", "site",
                           "channel", "article", "feed")
