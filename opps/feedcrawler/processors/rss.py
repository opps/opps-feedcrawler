# -*- coding:utf-8 -*-
import feedparser
import logging
import pytz
import json

from datetime import datetime
from time import mktime

from django.conf import settings
from django.utils import html
from django.utils import timezone
from django.utils.text import slugify

from .base import BaseProcessor

logger = logging.getLogger()


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

    def _get_entry_main_image(self, entry):
        for link in getattr(entry, 'links', []):
            if link.get('rel') == 'enclosure' and link.get(
                    'type', '').startswith('image'):
                return link.get('href')
        return False

    def _get_entry_description(self, entry):
        # Lots of entries are missing description_detail attributes.
        # Escape their content by default
        if hasattr(entry, 'description_detail') and\
                entry.description_detail.type != 'text/plain':
            return entry.description
        return html.escape(entry.description)

    def _get_entry_content(self, entry):
        if not hasattr(entry, 'content'):
            return None

        content = entry.content

        if isinstance(content, list):
            if not content:
                return None
            content = entry.content[0]

        if content.type == 'text/plain':
            return html.escape(content.value)

        return content.value

#        except Exception, e:
#            msg = 'Feedcrawler refresh_feeds. Entry "{}" content error'
#            logger.warning(msg.format(msg))

    def create_entries(self):
        created_count = 0
        updated_count = 0
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

            updated = False

            if created or not db_entry.main_image_id:
                main_image_url = self._get_entry_main_image(entry)
                if main_image_url:
                    db_entry.define_main_image(archive_link=main_image_url)
                    updated = True

            if created or not db_entry.entry_description:
                desc = _get_entry_description(entry)
                if desc:
                    db_entry.entry_description = desc
                    updated = True

            if created or not db_entry.entry_content:
                try:
                    content = _get_entry_content(entry)
                    if content:
                        db_entry.entry_content = content
                        updated = True
                except Exception as e:
                    msg = 'Feedcrawler refresh_feeds. Entry "%s" content error'
                    logger.warning(msg % (entry.link))

            if created:
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

                try:
                    allowed = (str, unicode, dict, list, int, float, long)
                    entry_source = json.dumps(
                        {k: v for k, v in entry.iteritems()
                            if isinstance(v, allowed)})
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

                if self.verbose:
                    print("Entry created %s" % db_entry.title)

            if created or updated:
                db_entry.save()
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        if self.verbose:
            print("%d entries created" % created_count)
            print("%d entries updated" % updated_count)

        return created_count

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
