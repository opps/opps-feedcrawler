# -*- coding: utf-8 -*-
from django.db import models
from opps.core.models import Publishable, BaseConfig
from django.utils.translation import ugettext_lazy as _


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


class Feed(Publishable):
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

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    def num_unread(self):
        return len(Entry.objects.filter(feed=self, read=False))

    def save(self, *args, **kwargs):
        """Poll new Feed"""
        try:
            Feed.objects.get(xml_url=self.xml_url)
            super(Feed, self).save(*args, **kwargs)
        except Feed.DoesNotExist:
            super(Feed, self).save(*args, **kwargs)
            from .utils import refresh_feed
            refresh_feed(self)


class Entry(models.Model):
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
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=2000, blank=True, null=True)
    link = models.CharField(max_length=2000)
    description = models.TextField(blank=True, null=True)
    published_time = models.DateTimeField(auto_now_add=True)
    entry_source = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-published_time']
        verbose_name_plural = 'entries'

    def __unicode__(self):
        return self.title


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
