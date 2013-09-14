#coding: utf-8
import random
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
from .category_brasil import CATEGORY_BRASIL

from opps.articles.models import Post
from opps.channels.models import Channel
from opps.contrib.db_backend.postgres.base import DatabaseError
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
        print("updating feed")
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
            self.feed.title = html.escape(self.parsed.feed.title)[:150]
        else:
            self.feed.title = self.parsed.feed.title[:150]

        self.feed.link = self.feed.link or self.parsed.feed.link

        if self.parsed.feed.description_detail.type == 'text/plain':
            self.feed.description = html.escape(self.parsed.feed.description)
        else:
            self.feed.description = self.parsed.feed.description

        self.feed.last_polled_time = timezone.now()
        try:
            self.feed.save()
        except Exception as e:
            print str(e)

        if self.verbose:
            print("Feed object updated %s" % self.feed.last_polled_time)


        return len(self.parsed.entries)

    def create_entries(self):
        print "creating entry"
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

            print "will create entry"

            slug = slugify(self.feed.slug + "-" + entry_title[:100])

            exists = self.entry_model.objects.filter(slug=slug).exists()
            if exists:
                continue


            db_entry, created = self.entry_model.objects.get_or_create(
                entry_feed=self.feed,
                entry_link=entry.link,
                channel=self.feed.channel,
                title=entry_title[:140],
                slug=slug,
                entry_title=entry_title[:140],
                site=self.feed.site,
                user=self.feed.user,
                published=True,
                show_on_root_channel=True
            )

            print "created"
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
                # db_entry.slug = slugify(self.feed.slug + "-" + entry_title[:150])
                db_entry.headline = db_entry.entry_description
                # db_entry.short_title = db_entry.title
                # db_entry.hat = db_entry.title
                db_entry.save()
                count += 1

                if self.verbose:
                    print("Entry created %s" % db_entry.title)

                try:
                    self.verbose_print('creating post')
                    self.create_post(db_entry)
                except Exception as e:
                    print(str(e))

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
        print "fetching"
        if not self.fetch():
            logger.warning("Feed cannot be parsed")
            return 0

        print "updating"
        if not self.update_feed():
            logger.info("No entry returned")
            return 0

        print "creating entries"
        created_count = self.create_entries()
        self.delete_old_entries()
        return created_count

    def get_channel_by_slug(self, slug):
        if not slug:
            return

        try:
            return Channel.objects.filter(long_slug=slug)[0]
        except:
            return

    def create_post(self, entry):
        # match category X channel
        channel_slug = CATEGORY_BRASIL.get(self.feed.source_url)
        channel = self.get_channel_by_slug(channel_slug)



        post = Post(
            title=entry.entry_title,
            slug=slugify(entry.entry_title),
            content=entry.entry_content or entry.entry_description,
            channel=channel or entry.channel,
            site=entry.site,
            user=entry.user,
            show_on_root_channel=True,
            published=True,
            # hat=entry.hat,
        )

        if self.feed.group:
            post.source = self.feed.group.name

        try:
            post.save()
        except DatabaseError:
            print "slug exists"
            # post.slug = u"{0}-{1}".format(random.getrandbits(32),
            #                               post.slug[:100])
            # post.save()
            return

        entry.post_created = True
        entry.save()

        self.verbose_print(u"Post {p.id}{p.title} created".format(p=post))

        return post
