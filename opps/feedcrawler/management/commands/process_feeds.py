# coding: utf-8
"""
This command polls all of the Feeds and inserts any new entries found.
"""
import logging
from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from opps.feedcrawler.models import Feed


logger = logging.getLogger('opps.feedcrawler')


class Command(BaseCommand):
    args = 'none'
    help = 'run the feed processor for every published feed.'
    option_list = BaseCommand.option_list + (
        make_option(
            '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='Print progress on command line'
        ),
        make_option(
            '--feed',
            dest='feed',
            default=False,
            help='Process only specified feed'
        ),
    )

    def handle(self, *args, **options):
        """
        Read through all the feeds looking for new entries.
        """
        verbose = options.get('verbose')
        feed_slug = options.get('feed')

        if feed_slug:
            feeds = Feed.objects.filter(slug=feed_slug)
        else:
            feeds = Feed.objects.filter(published=True)

        num_feeds = feeds.count()

        if verbose:
            self.stdout.write('%d feeds to process' % (num_feeds))

        for i, feed in enumerate(feeds):
            try:
                with transaction.commit_manually():
                    if verbose:
                        self.stdout.write(
                            '(%d/%d) Processing Feed %s'
                            % (i + 1, num_feeds, feed.title)
                        )

                    processor = feed.get_processor(verbose)
                    if processor:
                        if verbose:
                            self.stdout.write(
                                "Processing: %s" % processor.__class__)
                        try:
                            processor.process()
                        except Exception as e:
                            if verbose:
                                self.stderr.write(str(e))

                    transaction.commit()
            except Exception as e:
                msg = u"{f.title} - {msg}".format(f=feed, msg=str(e))
                logger.warning(msg)

        logger.info('Feedcrawler process_feeds completed successfully')
