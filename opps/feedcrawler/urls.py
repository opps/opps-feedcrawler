from django.conf.urls import patterns
from opps.feedcrawler.views import create_post

urlpatterns = patterns('',
    (r'^createpost/(?P<post_id>\d+)$', create_post, {}, 'create_post'),
)
