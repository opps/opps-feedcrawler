# -*- coding: utf-8 -*-
import json

from celery import task
from djcelery.models import PeriodicTask, IntervalSchedule
from django.utils import timezone
from opps.feedcrawler.management.commands.process_feeds import Command

from .models import Feed


def log_it(s):
    with open("/tmp/feedcrawler_task_run.log", "a") as log:
        msg = u"{} - {}\n".format(timezone.now(), s)
        log.write(msg.encode('utf-8'))


@task.periodic_task(run_every=timezone.timedelta(minutes=1))
def task_control():
    feeds = Feed.objects.all_published().filter(interval__gte=1)
    task_set = set()
    for feed in feeds:
        task_name = u'opps.feedcrawler.tasks_feed_{}'.format(feed.slug)
        interval, _ = IntervalSchedule.objects.get_or_create(
            every=feed.interval,
            period='minutes'
        )
        args = json.dumps([feed.slug, ])
        task, created = PeriodicTask.objects.get_or_create(
            name=task_name,
            defaults={
                'task': 'opps.feedcrawler.tasks.process_feed',
                'interval': interval,
                'args': args
            }
        )
        if created:
            log_it('Adding task {}'.format(task.name))

        if not created:
            changed = False
            if task.interval != interval:
                changed = True
                task.interval = interval
            if task.args != args:
                changed = True
                task.args = args
            if changed:
                log_it('Updating task {}'.format(task.name))
                task.save()

        task_set.add(task.name)

    # Remove inexistent feeds
    tasks_to_remove = PeriodicTask.objects.filter(
        name__startswith='opps.feedcrawler.tasks_feed'
    ).exclude(name__in=task_set)

    for task in tasks_to_remove:
        log_it('Updating task {}'.format(task.name))
        task.delete()


@task
def process_feed(feed_slug):
    command = Command()
    options = {'feed': feed_slug}
    log_it('Running {}'.format(feed_slug))
    command.handle(**options)
