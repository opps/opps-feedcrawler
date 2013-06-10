# -*- coding: utf-8 -*-
from opps.feedcrawler.models import Feed, Entry, FeedConfig
from opps.feedcrawler.utils import refresh_feed

from celery.decorators import periodic_task
from celery.task.schedules import crontab

import logging
logger = logging.getLogger()


@periodic_task(run_every=crontab(hour="*", minute=59, day_of_week="*"))
def refresh_feeds():
    """
    This command polls all of the Feeds and inserts any new entries found.

    """
    feeds = Feed.objects.all()
    for i, feed in enumerate(feeds):
        refresh_feed(feed)
        # Remove older entries
        entries = Entry.objects.filter(entry_feed=feed)
        max_entries_saved = FeedConfig.get_value('max_entries_saved') or 100
        if max_entries_saved:
            entries = entries[max_entries_saved:]
        for entry in entries:
            entry.delete()
    logger.info('feedcrawler refresh_feeds completed successfully')
