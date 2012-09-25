New Agenda
----------
Reworked agenda module by sb@feinheit.ch. original agenda by ssc and sb

The backend is uncoupled from the view function and can be replaced by the 
Facebook Event.



Usage
=====

- add :mod:`elephantagenda` and :mod:`elephantagenda.backends.default`  to
your :mod:`settings.INSTALLED_APPS`
- you can either use the :class:`elephantagenda.models.EventsContent` or
  add :mod:`elephantagenda.urls` as FeinCMS Application

**hint:** use the application, if you want to have a detail page with own url for every event.
if you just want to display a simple eventlist, use the content. 

To use the Facebook backend, simply add :mod:`elephantagenda.backends.fb_agenda`  to your
:mod:`settings.INSTALLED_APPS` instead.
