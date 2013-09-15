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

    def record_log(self, s):
        if not s:
            return
        if not isinstance(s, (str, unicode)):
            s = unicode(s)
        try:
            self.log_model.objects.create(
                feed=self.feed,
                type="created",
                text=s[:255]
            )
            self.verbose_print("Process log created")
        except:
            self.verbose_print("Cant create log")

    def log_created(self, s):
        if not s:
            return
        if not isinstance(s, (str, unicode)):
            s = unicode(s)
        try:
            return self.log_model.objects.filter(
                type="created",
                text=s[:255],
                feed=self.feed
            ).exists()
        except Exception as e:
            self.verbose_print(str(e))
            self.verbose_print("Cant check if log is created")
            return
