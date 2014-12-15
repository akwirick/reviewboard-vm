from __future__ import unicode_literals

from django.conf.urls import patterns, url

from scoreboard.extension import Scoreboard


urlpatterns = patterns(
    'scoreboard.views',

    url(r'^$', 'configure'),
)