#coding=utf-8

from datetime import date, datetime, timedelta

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django import forms

from feincms.module.medialibrary.models import MediaFile
from feincms.templatetags.feincms_thumbnail import thumbnail

from feincms.utils.html import cleanse

from django_countries.fields import CountryField
from django.contrib.auth.models import User

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    now = datetime.now

class CategoryBase(models.Model):
    name = models.CharField(_('name'), max_length=50)
    slug = models.SlugField(_('slug'), unique=True)
    
    class Meta:
        abstract = True
        verbose_name = _('Event category')
        verbose_name_plural = _('Event categories')
    
    def __unicode__(self):
        return self.name

class Category(CategoryBase):
    class Meta(CategoryBase.Meta):
        abstract = False

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug' : ('name',)}



class EventManager(models.Manager):
    def get_query_set(self):
        return super(EventManager, self).get_query_set().select_related('venue')

    def public(self):
        return self.filter(privacy='OPEN')
    
    def upcoming(self):
        """ returns all upcoming and ongoing events """
        today = date.today()
        if now().hour < 6:
            today = today-timedelta(days=1)
        
        return self.public().filter(Q(start_time__gte=today) | Q(end_time__gte=today))
    
    def past(self):
        """ returns all past events """
        today = date.today()
        if now().hour < 6:
            today = today-timedelta(days=1)
        
        return self.public().filter(Q(start_time__lt=today) & Q(end_time__lt=today))

class Venue(models.Model):
    name = models.CharField(_('Location'), max_length=255)
    street = models.CharField(_('Street'), max_length=255, blank=True)
    city = models.CharField(_('City'), max_length=50, blank=True)
    state = models.CharField(_('State'), max_length=30, blank=True)
    zip = models.CharField(_('Zip'), max_length=10, blank=True)
    country = CountryField(_('Country'), blank=True, null=True, default='CH')
    latitude = models.DecimalField(_('Latitude'), blank=True, null=True, max_digits=12, decimal_places=9)
    longitude = models.DecimalField(_('Longitude'), blank=True, null=True, max_digits=12, decimal_places=9)
    
    class Meta:
        verbose_name = _('Venue')
        verbose_name_plural = _('Venues')
    
    def __unicode__(self):
        return u'%s, %s, %s' % (self.name, self.street, self.city)

class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'street', 'city', 'country')



PRIVACY_CHOICES = (('OPEN', _('open')),
                   ('CLOSED', _('closed')),
                   ('SECRET', _('private')),
)

class EventBase(models.Model):
    
    def __init__(self, *args, **kwargs):
        super(EventBase, self).__init__(*args, **kwargs)
        self.cleanse = getattr(settings, 'EVENT_CLEANSE', False)
        cm = getattr(settings, 'CLEANSE_MODULE', None)
        if cm:
            try:
                self.cleanse_module = __import__(cm, fromlist=True)
            except (ValueError, ImportError):
                raise ImproperlyConfigured, 'There was an error importing your %s cleanse_module!' % self.__name__
        else:
            self.cleanse_module = cleanse
        self.meta = {'uses_medialibrary': True, 'editable': True }
            
    owner = models.ForeignKey(User, blank=True, null=True, verbose_name=_('Owner'), 
                              related_name='owns_%(app_label)s_%(class)s')
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    start_time = models.DateTimeField(_('Start time'), help_text=_('Start Datum und Zeit'))
    end_time = models.DateTimeField(_('End time'), blank=True, null=True, help_text=_('leave blank for full day events'))
    # location = models.CharField(_('Location'), max_length=255)
    privacy = models.CharField(_('Privacy'), max_length=10, choices=PRIVACY_CHOICES)
    updated_time = models.DateTimeField(_('updated time'), auto_now=True)
    
    picture = models.ForeignKey(MediaFile, blank=True, null=True,
                                related_name="%(app_label)s_%(class)s_events")

    # custom fields:    
    slug = models.SlugField(_('Slug'), max_length=100)
    language = models.CharField(_('Language'), max_length=5, choices=settings.LANGUAGES)
    
    objects = EventManager()

    class Meta:
        abstract = True
        ordering = ['-start_time']
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        #connections = ['feed', 'invited', 'attending', 'maybe', 'noreply', 'declined', 'picture']
        
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.start_time)
    
    def clean(self):        
        #an event cannot end before start
        if self.end_time and self.end_time <= self.start_time:
            raise ValidationError(_('The Event cannot end before start (Start date <= End date)'))
        
    @property
    def location(self):
        return self.venue.name
    
    @models.permalink
    def get_absolute_url(self):
        #TODO: Make this work
        return ('event_detail', (), {'id': self.id })
    
    
class Event(EventBase):
    venue = models.ForeignKey(Venue)
    categories = models.ManyToManyField(Category, blank=True, null=True, 
                            related_name="%(app_label)s_%(class)s_related")

    
    class Meta(EventBase.Meta):
        abstract = False


class EventAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'description': forms.widgets.Textarea(attrs={'class':'tinymce'}),
        }

class EventAdmin(admin.ModelAdmin):
    def thumb(self, obj):
        try:
            return u'<img src="%s" >' % thumbnail(obj.image, '200x60')
        except ValueError:
            return u'No Image'
    thumb.allow_tags = True

    form = EventAdminForm

    class Media:
        js = ('//ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js',
              settings.FEINCMS_RICHTEXT_INIT_CONTEXT['TINYMCE_JS_URL'],
              'tinymce_admin/init.js',
            )

    picture = forms.ModelChoiceField(queryset=MediaFile.objects.filter(type='image'),
                    label=_('media file'), required=False)

    save_on_top = True
    list_display=('__unicode__', 'start_time', 'end_time', 'privacy',
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
