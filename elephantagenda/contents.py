from django import forms
from django.core.paginator import Paginator

from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from .models import Venue, Event, Category

from django.db import models


class EventsContent(models.Model):
    filter = models.CharField(max_length=1, choices=(
        ('a', _('all')),
        ('u', _('upcoming')),
        ('p', _('past')),
    ))
    category = models.ForeignKey(Category, null=True, blank=True,
                                 help_text=_('Leave blank for all categories.'))

    class Meta:
        abstract = True
        verbose_name = _('event list')
        verbose_name_plural = _('event lists')

    @property
    def media(self):
        media = forms.Media()
        media.add_js(('lib/jquery.scrollTo-min.js',
                      'lib/fancybox/jquery.fancybox-1.3.4.pack.js'))
        media.add_css({'all': ('lib/fancybox/jquery.fancybox-1.3.4.css', )})

        return media

    def render(self, request, context, **kwargs):
        if self.filter == 'u':
            events = Event.objects.upcoming().order_by('start_time')
        elif self.filter == 'p':
            events = Event.objects.past().order_by('-start_time')
        else:
            events = Event.objects.all().order_by('start_time')

        if hasattr(self.parent, 'language'):
            events = events.filter(language=self.parent.language)
        if self.category:
            events = events.filter(categories=self.category)

        current_page = request.GET.get('page', 1)
        page = Paginator(events, 10).page(current_page)

        return render_to_string('content/agenda/event_list.html',
                                {'object_list': events, 'page': page, },
                                context_instance=RequestContext(request))


class EventMapContent(models.Model):
    filter = models.CharField(max_length=1, choices=(
        ('a', _('all')),
        ('u', _('upcoming')),
        ('p', _('past')),
    ))

    class Meta:
        abstract = True
        verbose_name = _('event map')
        verbose_name = _('event maps')

    @property
    def media(self):
        media = forms.Media()
        media.add_js(('http://maps.google.com/maps/api/js?sensor=false',
                      '/media/js/event_map.js'))
        media.add_css({'all': ('/media/css/event_map.css', )})
        return media

    def render(self, request, context, **kwargs):
        return render_to_string(
            'content/agenda/event_map.html',
            context_instance=RequestContext(request))
