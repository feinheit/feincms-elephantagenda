""" This module requires the django_gmapsfield from:
    https://github.com/sbaechler/django_gmapsfield
    and django-countries
"""

from ..agenda.models import EventBase, CategoryBase
from django.db import models
from gmapsfield.fields import GoogleMapsField
from django_countries.fields import CountryField
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin


class Venue(models.Model):
    name = models.CharField(_('Location'), max_length=255)
    street = models.CharField(_('Street'), max_length=255, blank=True)
    city = models.CharField(_('City'), max_length=50, blank=True)
    state = models.CharField(_('State'), max_length=30, blank=True)
    zip = models.CharField(_('Zip'), max_length=10, blank=True)
    country = CountryField(_('Country'), blank=True, null=True, default='CH')
    map = GoogleMapsField()

    class Meta:
        verbose_name = _('Venue')
        verbose_name_plural = _('Venues')

    def __unicode__(self):
        return u'%s, %s, %s' % (self.name, self.street, self.city)


class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'street', 'city', 'country')


class Category(CategoryBase):

    class Meta(CategoryBase.Meta):
        abstract = False


class Event(EventBase):
    venue = models.ForeignKey(Venue)
    categories = models.ManyToManyField(Category, blank=True, null=True,
                                        related_name="%(app_label)s_%(class)s_related")

    class Meta(EventBase.Meta):
        abstract = False
