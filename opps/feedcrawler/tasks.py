# coding: utf-8
import celery
from django.utils import timezone
from opps.feedcrawler.management.commands.process_feeds import Command

@celery.task(run_every=timezone.timedelta(minutes=60))
def process_feeds():
    command = Command()
    command.handle()
