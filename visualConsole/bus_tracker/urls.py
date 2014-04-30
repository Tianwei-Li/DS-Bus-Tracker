from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from django.conf import settings


urlpatterns = patterns('bus_tracker.views',
    (r'^$', 'index'),
    (r'visualization/', 'visualization'),
    (r'simulate/$', 'simulate'),
    #(r'^(?P<poll_id>\d+)/results/$', 'results'),
    #(r'^(?P<poll_id>\d+)/vote/$', 'vote'),
)

