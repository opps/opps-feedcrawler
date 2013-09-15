# coding: utf-8
import celery
# from celery.task.schedules import crontab
from django.utils import timezone
from opps.feedcrawler.management.commands.process_feeds import Command

# @celery.task(run_every=crontab(hour="*", minute="30", day_of_week="*"))
@celery.task.periodic_task(run_every=timezone.timedelta(minutes=20))
def process_feeds():
    command = Command()
    command.handle()
    try:
        import datetime
        open("/tmp/feedcrawler_task_run.log", "a").write(
            u"{now} - process_feeds\n".format(now=datetime.datetime.now())
        )
    except:
        pass

