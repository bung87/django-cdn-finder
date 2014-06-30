django-cdn-finder
=================
inspired by[django-remote-finder](https://github.com/garrison/django-remote-finder),but not a staticfiles finder.

###Installation


Add django-cdn-finder to `INSTALLED_APPS` in your settings:

    'cdn_finder',

###Usage
Get started by adding the following to ``settings.py``::

    CDN_FINDER_DIR = os.path.join(PROJECT_ROOT, 'assets')
    CDN_FINDER_PREFIX ='http://libs.useso.com/'

And then e.g. in a template, you can write::

     {% load static from cdn_finder_tags  %}
      <link rel="stylesheet" href="{% static 'http://necolas.github.com/normalize.css/3.0.1/normalize.css' %}" />
      <script src="{% static 'js/modernizr/2.8.2/modernizr.min.js' %}"></script>

No more need to keep such files in the repository!  ``./manage.py
runserver`` (with ``DEBUG=True``) will download the files as needed, as
will ``./manage.py collectstatic``.