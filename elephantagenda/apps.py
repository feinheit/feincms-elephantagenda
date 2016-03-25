from django.utils.translation import ugettext_lazy as _

from django.apps import AppConfig


class AgendaConfig(AppConfig):
    name = 'elephantagenda'
    verbose_name = _("agenda")
