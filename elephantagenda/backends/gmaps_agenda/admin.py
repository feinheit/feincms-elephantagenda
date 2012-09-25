from django.contrib import admin

from ..agenda.models import EventAdmin, CategoryAdmin
from .models import Event, Category, Venue, VenueAdmin

admin.site.register(Category, CategoryAdmin)

admin.site.register(Venue, VenueAdmin)

admin.site.register(Event, EventAdmin)