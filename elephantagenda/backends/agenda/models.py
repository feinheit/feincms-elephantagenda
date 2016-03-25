# coding=utf-8

from datetime import date, datetime, timedelta

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from feincms.templatetags.feincms_thumbnail import thumbnail
from feincms.translations import (TranslatedObjectManager,
                                  TranslatedObjectMixin, Translation)

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    now = datetime.now


@python_2_unicode_compatible
class CategoryBase(models.Model):
    name = models.CharField(_('name'), max_length=50)
    slug = models.SlugField(_('slug'), unique=True)

    class Meta:
        abstract = True
        verbose_name = _('Event category')
        verbose_name_plural = _('Event categories')

    def __str__(self):
        return self.name


class Category(CategoryBase):

    class Meta(CategoryBase.Meta):
        abstract = False


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class EventManager(TranslatedObjectManager):

    def get_query_set(self):
        return super(EventManager, self).get_query_set().select_related('venue')

    def public(self):
        return self.filter(privacy='OPEN')

    def upcoming(self):
        """ returns all upcoming and ongoing events """
        today = date.today()
        if now().hour < 6:
            today = today - timedelta(days=1)

        return self.public().filter(Q(start_time__gte=today) | Q(end_time__gte=today))

    def past(self):
        """ returns all past events """
        today = date.today()
        if now().hour < 6:
            today = today - timedelta(days=1)

        return self.public().filter(Q(start_time__lt=today) & Q(end_time__lt=today))


@python_2_unicode_compatible
class Venue(models.Model):
    name = models.CharField(_('Location'), max_length=255)
    street = models.CharField(_('Street'), max_length=255, blank=True)
    city = models.CharField(_('City'), max_length=50, blank=True)
    state = models.CharField(_('State'), max_length=30, blank=True)
    zip = models.CharField(_('Zip'), max_length=10, blank=True)
    country = CountryField(_('Country'), blank=True, null=True, default='CH')
    latitude = models.DecimalField(
        _('Latitude'), blank=True, null=True, max_digits=12, decimal_places=9)
    longitude = models.DecimalField(
        _('Longitude'), blank=True, null=True, max_digits=12, decimal_places=9)

    class Meta:
        verbose_name = _('Venue')
        verbose_name_plural = _('Venues')

    def __str__(self):
        return u'%s, %s, %s' % (self.name, self.street, self.city)


class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'street', 'city', 'country')


PRIVACY_CHOICES = (('OPEN', _('open')),
                   ('CLOSED', _('closed')),
                   ('SECRET', _('private')),
                   )


@python_2_unicode_compatible
class EventBase(models.Model, TranslatedObjectMixin):

    def __init__(self, *args, **kwargs):
        super(EventBase, self).__init__(*args, **kwargs)
        self.cleanse = getattr(settings, 'EVENT_CLEANSE', False)
        self.meta = {'uses_medialibrary': True, 'editable': True}

    owner = models.ForeignKey(User, blank=True, null=True, verbose_name=_('Owner'),
                              related_name='owns_%(app_label)s_%(class)s')
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    start_time = models.DateTimeField(
        _('Start time'), help_text=_('Start Datum und Zeit'))
    end_time = models.DateTimeField(_('End time'), blank=True, null=True, help_text=_(
        'leave blank for full day events'))
    # location = models.CharField(_('Location'), max_length=255)
    privacy = models.CharField(
        _('Privacy'), max_length=10, choices=PRIVACY_CHOICES)
    updated_time = models.DateTimeField(_('updated time'), auto_now=True)

    picture = models.ForeignKey(settings.AGENDA_MEDIA_FILE, blank=True, null=True,
                                related_name="%(app_label)s_%(class)s_events")

    # custom fields:
    slug = models.SlugField(_('Slug'), max_length=100)
    language = models.CharField(
        _('Language'), max_length=5, choices=settings.LANGUAGES)

    objects = EventManager()

    class Meta:
        abstract = True
        ordering = ['start_time']
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        #connections = ['feed', 'invited', 'attending', 'maybe', 'noreply', 'declined', 'picture']

    def __str__(self):
        return u'%s (%s)' % (self.name, self.start_time)

    def clean(self):
        # an event cannot end before start
        if self.end_time and self.end_time <= self.start_time:
            raise ValidationError(
                _('The Event cannot end before start (Start date <= End date)'))

    @property
    def location(self):
        return self.venue.name

    @models.permalink
    def get_absolute_url(self):
        return ('event_detail', (self.slug,), {})


class Event(EventBase):
    venue = models.ForeignKey(Venue)
    categories = models.ManyToManyField(Category, blank=True,
                                        related_name="%(app_label)s_%(class)s_related")

    class Meta(EventBase.Meta):
        abstract = False


class EventTranslation(Translation(Event)):
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Event Translation')
        verbose_name_plural = _('Event Translations')


class EventAdminForm(forms.ModelForm):

    class Meta:
        widgets = {
            'description': forms.widgets.Textarea(attrs={'class': 'tinymce'}),
        }


class EventTranslationInline(admin.TabularInline):
    model = EventTranslation
    max_num = len(settings.LANGUAGES)


class EventAdmin(admin.ModelAdmin):

    def thumb(self, obj):
        try:
            return u'<img src="%s" >' % thumbnail(obj.picture, '200x60')
        except ValueError:
            return u'No Image'
    thumb.allow_tags = True

    form = EventAdminForm

    inlines = [EventTranslationInline]

    save_on_top = True
    list_display = ('__str__', 'start_time', 'end_time', 'privacy',
                    'location', 'thumb')
    fieldsets = [
        (None, {
            'fields': ('privacy',  'start_time',  'end_time',
                       'name', 'slug', 'description', 'language',
                       'picture', 'venue', 'categories')
        }),
    ]
    list_filter = ('start_time', 'privacy')
    raw_id_fields = ('picture', 'venue')
    prepopulated_fields = {'slug': ('name',)}
