from django.http import JsonResponse
from django.forms.models import model_to_dict
from feincms.views.decorators import standalone

from .models import Event


@standalone
def events(request):
    filter = request.GET.get('filter', 'upcoming')

    if filter == 'past':
        events = Event.objects.past()
    elif filter == 'active':
        events = Event.objects.active()
    elif filter == 'all':
        events = Event.objects.all()
    else:
        events = Event.objects.upcoming()

    return JsonResponse(
        [model_to_dict(ev) for ev in events],
        safe=False)
