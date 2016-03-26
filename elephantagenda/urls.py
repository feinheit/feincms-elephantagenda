from api import events
from django.conf.urls import *

from .views import EventArchiveview, EventDetailView, EventListView

urlpatterns = patterns('',
                       url(r'^$', EventListView.as_view(),
                           name='event_list'),
                       url(r'^(?P<slug>[\w-]+)/$', EventDetailView.as_view(),
                           name='event_detail'),
                       url(r'^archive/$', EventArchiveview.as_view(),
                           name='event_list'),

                       url('^api/events/', events, name='api_events'),
                       )
