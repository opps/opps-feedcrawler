# coding: utf-8

from opps.feedcrawler.models import Entry, ProcessLog


class BaseProcessor(object):
    def __init__(self, feed, entry_model=None, log_model=None,
                 verbose=False, *args, **kwargs):
        self.feed = feed
        self.entry_model = entry_model or Entry
        self.log_model = log_model or ProcessLog
        self.args = args
        self.kwargs = kwargs
        self.verbose = verbose

    def process(self):
        raise NotImplementedError(u"You should override this method")

    def __call__(self):
        return self.process()

    def verbose_print(self, s):
        if self.verbose:
            print(s)
