from django.template.base import Node
from django.utils.six.moves.urllib.parse import urljoin
from django.templatetags.static import PrefixNode
from django.conf import settings
from django import template
from django.utils.six.moves.urllib.parse import urlparse
register = template.Library()

class StaticNode(Node):
    def __init__(self, varname=None, path=None):
        if path is None:
            raise template.TemplateSyntaxError(
                "Static template nodes must be given a path to return.")
        self.path = path
        self.varname = varname
    @classmethod
    def resolve(self,path):
        path_str=str(path)
        if  not path_str.startswith('http://') and not  path_str.startswith('https://') and not path_str.startswith('//'):
            parts=path_str.split('/')
            return parts[0]+"/"+"".join(parts[3:])
        else:
            parse_result=urlparse(str(path))
            path_str=parse_result.path
            parts=path_str.split('/')
            fname=''.join(parts[-1:])
            if fname.index('.css')!=-1:
                return 'css/'+fname
            elif fname.index('.js')!=-1:
                return 'js/'+fname
            elif fname.index('.jpg')!=-1 or fname.index('.png')!=-1 or fname.index('.gif')!=-1:
                return 'images/'+fname

    def url(self, context):
        path = self.path.resolve(context)
        save_path=StaticNode.resolve(path)
        if settings.DEBUG == True:
            CDNFinder().find(path,save_path)
        return urljoin(PrefixNode.handle_simple("STATIC_URL"),save_path)

    def render(self, context):
        url = self.url(context)
        if self.varname is None:
            return url
        context[self.varname] = url
        return ''

    @classmethod
    def handle_token(cls, parser, token):
        """
        Class method to parse prefix node and return a Node.
        """
        bits = token.split_contents()

        if len(bits) < 2:
            raise template.TemplateSyntaxError(
                "'%s' takes at least one argument (path to file)" % bits[0])

        path = parser.compile_filter(bits[1])
        if len(bits) >= 2 and bits[-2] == 'as':
            varname = bits[3]
        else:
            varname = None

        return cls(varname, path)
@register.tag('static')
def do_static(parser, token):
    """
    Joins the given path with the STATIC_URL setting.

    Usage::

        {% static path [as varname] %}

    Examples::

        {% static "myapp/css/base.css" %}
        {% static variable_with_path %}
        {% static "myapp/css/base.css" as admin_base_css %}
        {% static variable_with_path as varname %}

    """
    return StaticNode.handle_token(parser, token)

import logging
from django.utils.six.moves.urllib.request import urlopen
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.finders import BaseFinder
import os

logger = logging.getLogger(__name__)

class CDNFinder(BaseFinder):
    def __init__(self):
        self.cache_dir = getattr(settings, "CDN_FINDER_DIR", None)
        self.cdn_prefix= getattr(settings, "CDN_FINDER_PREFIX", None)
        if not self.cache_dir:
            raise ImproperlyConfigured("settings.CDN_FINDER_DIR must point to a cache directory.")
        self.storage = FileSystemStorage(self.cache_dir)

    def find(self, path,save_path, all=False):

        self.fetch(path,save_path)
        match = self.storage.path(save_path)
        if all:
            return [match]
        else:
            return match

    def fetch(self, path,save_path):
        if self.storage.exists(save_path):
            length=os.path.getsize ( os.path.join(self.cache_dir,save_path))
            if length>100:
                return

            self.storage.delete(save_path)

        # download the file
        path_str=str(path)
        if  not path_str.startswith('http://') and not  path_str.startswith('https://') and not path_str.startswith('//'):
            url=self.cdn_prefix+path
        else:
            url=path
        logger.debug("Downloading %s", url)

        response = urlopen(url)
        if response.info().get('Content-Encoding') == 'gzip':
            from StringIO import StringIO
            import gzip
            buf = StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            try:
                content = f.read().decode('utf-8')
            finally:
                f.close()
        else:
            content = response.read()
        logger.debug("status: %s", response.code)
        logger.debug("%s", response.info())

        # save it
        if content :
            name = self.storage.save(save_path, ContentFile(content))
            if str(name) != path:
                logger.warning("Save failed: %r != %r", name, save_path)

    def list(self, ignore_patterns):
        raise NotImplementedError