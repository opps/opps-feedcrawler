# coding: utf-8
"""
This command polls all of the Feeds and inserts any new entries found.
"""
from optparse import make_option
from django.core.management.base import BaseCommand
from feedreader.models import Feed, Entry, FeedConfig
from feedreader.utils import refresh_feed

import logging
logger = logging.getLogger('feedreader')


class Command(BaseCommand):
    args = 'none'
    help = 'Polls all Feeds for Entries.'
    option_list = BaseCommand.option_list + (
        make_option(
            '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='Print progress on command line'
        ),
    )

    def handle(self, *args, **options):
        """
        Read through all the feeds looking for new entries.
        """
        verbose = options['verbose']
        feeds = Feed.objects.all()
        num_feeds = len(feeds)
        if verbose:
            print('%d feeds to process' % (num_feeds))
        for i, feed in enumerate(feeds):
            if verbose:
                print('(%d/%d) Processing Feed %s' % (i + 1, num_feeds, feed.title))
            refresh_feed(feed, verbose)
            # Remove older entries
            entries = Entry.objects.filter(feed=feed)
            max_entries_saved = FeedConfig.get_value('max_entries_saved')
            if max_entries_saved:
                entries = entries[max_entries_saved:]
            for entry in entries:
                entry.delete()
            if verbose:
                print('Deleted %d entries from feed %s' % ((len(entries), feed.title)))
        logger.info('Feedreader refresh_feeds completed successfully')
