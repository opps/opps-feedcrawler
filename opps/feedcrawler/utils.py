# coding: utf-8
import feedparser
import pytz
import json
import uuid
from datetime import datetime
from time import mktime
from django.conf import settings
from django.utils import html
from django.utils import timezone
from django.utils.text import slugify
from .models import Entry, FeedConfig


import logging
logger = logging.getLogger('feedreader')


def refresh_feed(db_feed, verbose=False):
    """
    Read through a feed looking for new entries.
    """
    # options = Options.objects.all()
    # if options:
    #     options = options[0]
    # else:  # Create options row with default values
    #     options = Options.objects.create()
    parsed = feedparser.parse(db_feed.xml_url)
    if hasattr(parsed.feed, 'bozo_exception'):
        # Malformed feed
        msg = 'FeedCrawler refresh_feeds found Malformed feed, %s: %s'
        logger.warning(msg % (db_feed.xml_url, parsed.feed.bozo_exception))
        if verbose:
            print(msg)
        return
    if hasattr(parsed.feed, 'published_parsed'):
        published_time = datetime.fromtimestamp(
            mktime(parsed.feed.published_parsed)
        )

        published_time = pytz.timezone(
            settings.TIME_ZONE
        ).localize(
            published_time,
            is_dst=None
        )

        if db_feed.published_time and db_feed.published_time >= published_time:
            return
        db_feed.published_time = published_time

    for attr in ['title', 'title_detail', 'link',
                 'description', 'description_detail']:
        if not hasattr(parsed.feed, attr):
            msg = 'FeedCrawler refresh_feeds. Feed "%s" has no %s'
            logger.error(msg % (db_feed.xml_url, attr))
            if verbose:
                print(msg)
            return
    if parsed.feed.title_detail.type == 'text/plain':
        db_feed.title = html.escape(parsed.feed.title)
    else:
        db_feed.title = parsed.feed.title
    db_feed.link = parsed.feed.link
    if parsed.feed.description_detail.type == 'text/plain':
        db_feed.description = html.escape(parsed.feed.description)
    else:
        db_feed.description = parsed.feed.description
    db_feed.last_polled_time = timezone.now()
    db_feed.save()
    if verbose:
        msg = '%d entries to process in %s'
        print(msg % (len(parsed.entries), db_feed.title))

    max_entries_saved = FeedConfig.get_value(
        'max_entries_saved'
    ) or 100

    for i, entry in enumerate(parsed.entries):
        if i > max_entries_saved:
            break
        missing_attr = False
        for attr in ['title', 'title_detail', 'link', 'description']:
            if not hasattr(entry, attr):
                msg = 'Feedcrawler refresh_feeds. Entry "%s" has no %s'
                logger.error(msg % (entry.link, attr))
                if verbose:
                    print(msg)
                missing_attr = True
        if missing_attr:
            continue
        if entry.title == "":
            msg = 'Feedcrawler refresh_feeds. Entry "%s" has a blank title'
            logger.warning(msg % (entry.link))
            if verbose:
                print(msg)
            continue
        u_id = unicode(uuid.uuid4())
        db_entry, created = Entry.objects.get_or_create(
            entry_feed=db_feed,
            entry_link=entry.link,
            channel=db_feed.channel,
            title=u_id,
            slug=slugify(u_id),
            site=db_feed.site,
            user=db_feed.user,
            published=True
        )
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
            if entry.title_detail.type == 'text/plain':
                db_entry.entry_title = html.escape(entry.title)
            else:
                db_entry.entry_title = entry.title
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
                allowed = (str, unicode, dict, list)
                entry_source = json.dumps(
                    {k: v for k, v in entry.iteritems()
                        if isinstance(v, allowed)}
                )
                db_entry.entry_source = entry_source
            except Exception, e:
                print str(e)
                msg = 'Feedcrawler refresh_feeds. Entry "%s" json error'
                logger.warning(msg % (entry.link))

            # fill Article properties
            db_entry.title = db_entry.entry_title[:140]
            db_entry.slug = slugify(db_entry.entry_title[:150])
            db_entry.headline = db_entry.entry_description
            db_entry.short_title = db_entry.title
            db_entry.hat = db_entry.title
            db_entry.save()
