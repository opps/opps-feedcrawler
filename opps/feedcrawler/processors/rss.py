# -*- coding:utf-8 -*-
import feedparser
import logging
import pytz
import json
# import uuid

from datetime import datetime
from time import mktime

from django.conf import settings
from django.utils import html
from django.utils import timezone
from django.utils.text import slugify

from .base import BaseProcessor

logger = logging.getLogger()

OPPS_FEEDCRAWLER_USE_TITLE_KEY = getattr(
    settings, 'OPPS_FEEDCRAWLER_USE_TITLE_KEY', False)


class RSSProcessor(BaseProcessor):

    def fetch(self):
        self.parsed = feedparser.parse(self.feed.source_url)
        if hasattr(self.parsed.feed, 'bozo_exception'):
            msg = "Malformed feed %s" % self.feed.source_url
            logger.warning(msg)
            if self.verbose:
                print(msg)
            return

        if self.verbose:
            print("Feed succesfully parsed")

        return self.parsed

    def update_feed(self):
        if hasattr(self.parsed, 'published_parsed'):
            published_time = datetime.fromtimestamp(
                mktime(self.parsed.feed.published_parsed)
            )
            published_time = pytz.timezone(
                settings.TIME_ZONE
            ).localize(
                published_time,
                is_dst=None
            )

            if (self.feed.published_time and
                    self.feed.published_time >= published_time):
                return

            self.feed.published_time = published_time

        for attr in ['title', 'title_detail', 'link',
                     'description', 'description_detail']:
            if not hasattr(self.parsed.feed, attr):
                msg = 'refresh_feeds. Feed "%s" has no %s'
                logger.error(msg % (self.feed.source_url, attr))
                return

        if self.parsed.feed.title_detail.type == 'text/plain':
            self.feed.title = html.escape(self.parsed.feed.title)
        else:
            self.feed.title = self.parsed.feed.title

        self.feed.link = self.feed.link or self.parsed.feed.link

        if self.parsed.feed.description_detail.type == 'text/plain':
            self.feed.description = html.escape(self.parsed.feed.description)
        else:
            self.feed.description = self.parsed.feed.description

        self.feed.last_polled_time = timezone.now()
        self.feed.save()

        if self.verbose:
            print("Feed object updated %s" % self.feed.last_polled_time)

        return len(self.parsed.entries)

    def create_entries(self):
        count = 0
        for i, entry in enumerate(self.parsed.entries):
            if i > self.max_entries_saved:
                break
            missing_attr = False
            for attr in ['title', 'title_detail', 'link', 'description']:
                if not hasattr(entry, attr):
                    msg = 'Feedcrawler refresh_feeds. Entry "%s" has no %s'
                    logger.error(msg % (entry.link, attr))
                    missing_attr = True
            if missing_attr:
                continue
            if entry.title == "":
                msg = 'Feedcrawler refresh_feeds. Entry "%s" has a blank title'
                logger.warning(msg % (entry.link))
                continue

            if entry.title_detail.type == 'text/plain':
                entry_title = html.escape(entry.title)
            else:
                entry_title = entry.title

            if OPPS_FEEDCRAWLER_USE_TITLE_KEY:
                db_entry, created = self.entry_model.objects.get_or_create(
                    site=self.feed.site,
                    slug=slugify(self.feed.slug + "-" + entry_title[:150]),
                    defaults=dict(
                        entry_feed=self.feed,
                        entry_link=entry.link,
                        channel=self.feed.channel,
                        title=entry_title[:140],
                        entry_title=entry_title,
                        user=self.feed.user,
                        published=True,
                        show_on_root_channel=True
                    )
                )
            else:
                try:
                    db_entry = self.entry_model.objects.get(
                        entry_original_id=entry.id)
                    created = True
                except:
                    db_entry, created = self.entry_model.objects.get_or_create(
                        site=self.feed.site,
                        defaults=dict(
                            entry_feed=self.feed,
                            channel=self.feed.channel,
                            user=self.feed.user,
                            title=entry_title[:140],
                            entry_original_id=entry.id,
                            published=True,
                            show_on_root_channel=True
                        )
                    )
                try:
                    db_entry.site = self.feed.site,
                    db_entry.title = entry_title[:140]
                    db_entry.entry_title = entry_title
                    db_entry.slug = slugify(
                        self.feed.slug + "-" + entry_title[:150]),
                    db_entry.user = self.feed.user
                    db_entry.channel = self.feed.channel
                    db_entry.save()
                except Exception, e:
                    created = False
                    # logging
                    print str(e)
                    msg = 'Feedcrawler refresh_feeds. Entry "%s" content error'
                    logger.warning(msg % (entry.link))
            if created:
                if hasattr(entry, 'links'):
                    links = [
                        item for item in entry.links
                        if item.get('rel') == 'enclosure'
                    ]
                    for link in links:
                        if link.get('type', '').startswith('image'):
                            url = link.get('href')
                            db_entry.define_main_image(archive_link=url)

                if hasattr(entry, 'published_parsed'):
                    published_time = datetime.fromtimestamp(
                        mktime(entry.published_parsed)
                    )

                    published_time = pytz.timezone(
                        settings.TIME_ZONE
                    ).localize(
                        published_time,
                        is_dst=None
                    )

                    now = timezone.now()

                    if published_time > now:
                        published_time = now
                    db_entry.entry_published_time = published_time

                # Lots of entries are missing description_detail attributes.
                # Escape their content by default
                if hasattr(entry, 'description_detail') and \
                        entry.description_detail.type != 'text/plain':
                    db_entry.entry_description = entry.description
                else:
                    db_entry.entry_description = html.escape(entry.description)

                try:
                    content = None
                    if hasattr(entry, 'content'):
                        content = entry.content
                        if isinstance(content, list) and content:
                            content = entry.content[0]

                    if content and content.type != 'text/plain':
                        db_entry.entry_content = content.value
                    elif hasattr(entry, 'content'):
                        db_entry.entry_content = html.escape(content.value)
                except Exception, e:
                    print str(e)
                    msg = 'Feedcrawler refresh_feeds. Entry "%s" content error'
                    logger.warning(msg % (entry.link))

                try:
                    allowed = (str, unicode, dict, list, int, float, long)
                    entry_source = json.dumps(
                        {k: v for k, v in entry.iteritems()
                            if isinstance(v, allowed)}
                    )
                    db_entry.entry_json = entry_source
                    pass
                except Exception, e:
                    print str(e)
                    msg = 'Feedcrawler refresh_feeds. Entry "%s" json error'
                    logger.warning(msg % (entry.link))

                # fill Article properties
                db_entry.title = db_entry.entry_title[:140]
                db_entry.headline = db_entry.entry_description
                db_entry.short_title = db_entry.title
                db_entry.hat = db_entry.title
                db_entry.save()
                count += 1

                if self.verbose:
                    print("Entry created %s" % db_entry.title)

        if self.verbose:
            print("%d entries created" % count)
        return count

    def delete_old_entries(self):
        entries = self.entry_model.objects.filter(entry_feed=self.feed)
        entries = entries[self.max_entries_saved:]
        # Cannot use 'limit' or 'offset' with delete.
        for entry in entries:
            entry.delete()

        if self.verbose:
            print("%d entries deleted" % len(entries))

    def process(self):
        # fetch and parse the feed

        self.max_entries_saved = self.feed.max_entries or 1000
        if not self.fetch():
            logger.warning("Feed cannot be parsed")
            return 0

        if not self.update_feed():
            logger.info("No entry returned")
            return 0

        created_count = self.create_entries()
        self.delete_old_entries()
        return created_count
