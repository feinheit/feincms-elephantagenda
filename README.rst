Elephantagenda
--------------

A handy agenda module for FeinCMS.

The backend is uncoupled from the view function and can be replaced by the 
Facebook Event API.

The model structure is based on the Facebook Event module.

Usage
=====

- ``pip install elephantagenda[facebook]``
- setup your ``AGENDA_MEDIA_FILE`` which is path to your image field ``media.Image`` for example
- redirect migration using migration modules from django settings
- make migrations ``python manage.py makemigrations agenda``
- add ``elephantagenda`` and ``elephantagenda.backends.agenda``  to your ``settings.INSTALLED_APPS``
- you can either use the ``elephantagenda.models.EventsContent`` or add ``elephantagenda.urls`` as FeinCMS Application

**hint:** use the application, if you want to have a detail page with own url for every event.
if you just want to display a simple eventlist, use the content. 

To use the Facebook backend, simply add ``elephantagenda.backends.fb_agenda``  to your
``settings.INSTALLED_APPS`` instead.

Build
=====

- ``python setup.py sdist build``
- ``python setup.py sdist upload``

Requirements
============

 * https://github.com/feinheit/django-facebook-graph for ``fb_agenda``

 * https://github.com/sbaechler/django_gmapsfield for ``gmaps_agenda``

 * ``django-countries` for agenda and ``gmaps_agenda``