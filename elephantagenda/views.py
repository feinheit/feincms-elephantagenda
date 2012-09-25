from django.shortcuts import get_object_or_404
from django.template.context import RequestContext
from django.template.loader import render_to_string
from backends import get_backend 

from models import Event
from feincms.translations import short_language_code


def event_list(request, filter=None):
    if filter == 'upcoming':
        events = Event.objects.upcoming().filter(language=short_language_code)
    elif filter == 'past':
        events = Event.objects.past().filter(language=short_language_code)
    else:
        events = Event.objects.active().filter(language=short_language_code)
    
    return render_to_string('agenda/event_list.html', {'object_list' : events}, RequestContext(request))

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    return render_to_string('agenda/event_detail.html', {'object' : event}, RequestContext(request))