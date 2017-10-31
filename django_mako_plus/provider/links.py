from django.conf import settings

from ..util import merge_dicts
from .base import BaseProvider

import os
import os.path
import posixpath


class LinkProvider(BaseProvider):
    '''Base class for providers that create links'''
    # the default options are for CSS files
    default_options = merge_dicts(BaseProvider.default_options, {  
        'group': 'styles',
        'filename': '{appdir}/somedir/{template}.static.file',
    })
    def init(self):
        self.content = None
        fargs = {
            'appdir': self.app_dir, 
            'template': self.template_name,
        }
        fullpath = self.options['filename'].format(**fargs)
        if os.path.exists(fullpath):
            # the cgi_id is a unique number either given by the project or by reading the last modified time of the file
            # it is important to add to links (see make_link in the subclasses) because it makes the url unique, which
            # forces browsers to re-download the file despite a previous version being in their cache.  Without this id,
            # some browsers (Chrome, I'm looking at you) use the cached version even after updates to the file.
            if self.cgi_id is None:
                self.cgi_id = int(os.stat(fullpath).st_mtime)
            # make it relative to the project root, and ensure we have forward slashes (even on windows) because this is for urls
            href = posixpath.join(settings.STATIC_URL, os.path.relpath(fullpath, settings.BASE_DIR))  
            self.content = self.make_link(href)

    def make_link(href):
        raise NotImplementedError('Subclass should have implemented this.')

    def get_content(self, provider_run):
        return self.content


class CssLinkProvider(LinkProvider):
    '''Generates a CSS <link>'''
    default_options = merge_dicts(LinkProvider.default_options, { 
        'filename': '{appdir}/styles/{template}.css',
    })
    def make_link(self, href):
        return '<link rel="stylesheet" type="text/css" href="{}?{}" />'.format(href, self.cgi_id)


class JsLinkProvider(LinkProvider):
    '''Generates a JS <script>'''
    default_options = merge_dicts(LinkProvider.default_options, {  
        'group': 'scripts',
        'filename': '{appdir}/scripts/{template}.js',
    })
    def make_link(self, href):
        return '<script type="text/javascript" src="{}?{}"></script>'.format(href, self.cgi_id)

