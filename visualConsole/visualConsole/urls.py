from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^bus_tracker/', include('bus_tracker.urls')),
    (r'^admin/', include(admin.site.urls)),
)
