# coding: utf-8

from opps.feedcrawler.models import Entry


class BaseProcessor(object):
    def __init__(self, feed, entry_model=None, verbose=False, *args, **kwargs):
        self.feed = feed
        self.entry_model = entry_model or Entry
        self.args = args
        self.kwargs = kwargs
        self.verbose = verbose

    def process(self):
        raise NotImplementedError(u"You should override this method")

    def __call__(self):
        return self.process()
