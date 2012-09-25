""" Admin classes are in models due to use double import on other backends.
"""

from django.contrib import admin

from models import Event, EventAdmin, Category, CategoryAdmin, Venue, VenueAdmin


admin.site.register(Category, CategoryAdmin)

admin.site.register(Venue, VenueAdmin)

admin.site.register(Event, EventAdmin)

