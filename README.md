opps-feedcrawler
================

FeedCrawler takes a **feed** of any type, executes its customized processor in order to create CMS Entries.


Feed
====

Feed is commonly a url with some configurations, **url**, **credentials**, **processor** and **actions**

The most simple example is an RSS feed

- url = 'http://site.com/feed.rss'
- processor = 'opps.feedcrawler.processors.rss.RSSProcessor'
- actions = ['opps.feedcrawler.actions.rss.RSSActions'

In the above example we have an **url** to read feed entries, and feedcrawler comes with a builtin processor for RSS feeds
**RSSProcessor** wil take the feed url and do all the job fetching, reading and creating **entries** on database.

> You can replace RSSProcessor with your own processor class, following the processor API.   

> Example: 'yourproject.yourmodule.processors.MyProcessor'

> The processor API is documented in the item **Processor API**


Also, your **feed** takes **actions** which is a path to a callable returning a list of Django admin actions in the form of functions.
an example of action is "Create posts" which takes the selected entries and convert it in to Opps Posts.

Processor API
=============

feedcrawler provides a **BaseProcessor** class for you to extend and you have to override some methods.



    from opps.feedcrawler.processors.base import BaseProcessor
    
    class MyProcessor(BaseProcessor):
        """
        BaseProcessor.__init__ receives the **feed** object as parameter
        
        def __init__(feed, entry_model, *args, **kwargs):
            self.feed = feed
            self.entry_model = entry_model
            
        You override if you need, but be careful.
        """
       
        def process(self):
            url = self.feed.source_url
            max_entries = self.feed.max_entries
            ...
            
            # here you have access to the **feed** object in **self.feed**
            entries = read_and_parse_rss_feed(url)  #  example function which fetch and parse XML feed 
            
            # Now you have access to **self.entry_model** which you will use to create CMS entries.
            for entry in entries:
                # remember to implement your own logic to avoid duplications
                self.entry_model.objects.get_or_create(
                    title=entry['title']
                    ...
                    ...
                )
                
            # this method should return the count of entries read and created or 0    
            return len(entries)
            
            

The processor above will be executed by management command **manage.py process_feeds -f feed_slug** also you can put this command to run on **cron** or **celery**
