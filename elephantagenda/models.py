from django.conf import settings

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

""" Add the backend to settings.INSTALLED_APPS """

backend_models =  getattr(settings, 'AGENDA_BACKEND', 'elephantagenda.backends.agenda')

exec 'from %s.models import *' % backend_models

