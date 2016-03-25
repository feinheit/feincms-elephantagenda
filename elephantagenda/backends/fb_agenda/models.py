# coding=utf-8
import urllib
import urllib2
from datetime import date, datetime, timedelta

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from facebook.models import Event as EventFromFacebook
from facebook.utils import get_graph

if 'facebook' not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured, 'You have to add \'facebook\' to your INSTALLED_APPS before creating a FB Event'


class Category(models.Model):
    name = models.CharField(_('name'), max_length=50)
    slug = models.SlugField(_('slug'), unique=True)

    class Meta:
        verbose_name = _('Event category')
        verbose_name_plural = _('Event categories')

    def __unicode__(self):
        return self.name


class FBEventManager(models.Manager):

    def public(self):
        return self.filter(_privacy='OPEN')

    def upcoming(self):
        """ returns all upcoming and ongoing events """
        today = date.today()
        if datetime.now().hour < 6:
            today = today - timedelta(days=1)

        return self.public().filter(Q(_start_time__gte=today) | Q(_end_time__gte=today))

    def past(self):
        """ returns all past events """
        today = date.today()
        if datetime.now().hour < 6:
            today = today - timedelta(days=1)

        return self.active().filter(Q(_start_date__lt=today) & Q(_end_date__lt=today))

# FB Event Adapter class


class Event(EventFromFacebook):

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.meta = {'uses_medialibrary': False, 'editable': False}

    # custom fields:
    categories = models.ManyToManyField(
        Category, blank=True, null=True, related_name="%(app_label)s_%(class)s_related")
    language = models.CharField(
        _('Language'), max_length=5, choices=settings.LANGUAGES)
    image = models.ImageField(upload_to='event_images/%Y/%m', blank=True, null=True,
                              max_length=200)
    max_places = models.PositiveSmallIntegerField(
        _(u'Anzahl Plätze'), blank=True, null=True)
    # quick fix
    access_token = models.CharField(
        max_length=100, blank=True, help_text='for internal use only.')
    objects = FBEventManager()

    class Meta:
        proxy = False  # Add custom fields category, slug and language
        ordering = ['_start_time']
        verbose_name = _('fb event')
        verbose_name_plural = _('fb events')

    def __unicode__(self):
        return u'%s (%s)' % (self._name, self._start_time)

    def not_implemented(self, *args, **kwargs):
        raise NotImplementedError

    def get_from_facebook(self, graph=None, save=False):
        if self.access_token:
            graph = get_graph()
            graph.access_token = self.access_token
        super(Event, self).get_from_facebook(graph, save)
        if getattr(graph, 'access_token', None):
            params = urllib.urlencode(
                {'type': 'large', 'access_token': graph.access_token})
            url = 'https://graph.facebook.com/%s/picture/?%s' % (
                self.id, params)
            try:
                image = urllib2.urlopen(url).read()
            except urllib2.HTTPError as e:
                self.graph['image'] = e.__str__()
                self.save()
                return
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(image)
            img_temp.flush()
            self.image.save('%s.jpg' % self.slug, File(img_temp))

    def _owner(self):
        return self._owner
    owner = property(_owner, not_implemented)

    def _name(self):
        return self._name
    name = property(_name, not_implemented)

    @property
    def description(self):
        return self._description

    def _start_time(self):
        return self._start_time
    start_time = property(_start_time, not_implemented)

    def _end_time(self):
        return self._end_time
    end_time = property(_end_time, not_implemented)

    @property
    def location(self):
        return self._location

    @property
    def venue(self):
        return self._venue

    @property
    def privacy(self):
        return self._privacy

    @property
    def updated_time(self):
        return self._updated_time

    def _image(self):
        return self.image.url
        """
        if self._privacy == 'SECRET':
            return self.image.url
        else:
            return u'http://graph.facebook.com/%s/picture/?type=large' % self.id
        """
    picture = property(_image, not_implemented)

    @models.permalink
    def get_absolute_url(self):
        return self.facebook_link
