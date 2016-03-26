
from models import Event


from django.views.generic import DetailView, ListView


class EventListView(ListView):

    template_name = 'agenda/event_list.html'
    queryset = Event.objects.upcoming()
    paginate_by = 20


class EventArchiveview(EventListView):

    queryset = Event.objects.past()


class EventDetailView(DetailView):

    model = Event
    template_name = 'agenda/event_detail.html'
