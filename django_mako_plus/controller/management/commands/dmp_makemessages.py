from django import VERSION as django_version
from django.core.management.base import BaseCommand, CommandError
from django.utils.importlib import import_module
from django.core.management.commands.makemessages import Command as MakeMessagesCommand
from django.conf import settings
from django.utils.importlib import import_module
from django_mako_plus.controller.router import _get_dmp_apps, MakoTemplateRenderer
from optparse import make_option
import os, os.path, shutil, fnmatch, glob


class Command(MakeMessagesCommand):
  help = "Makes messages for Mako templates.  The native makemessages in Django doesn't understand Mako files, so this command compiles all your templates so it can find the compiled .py versions of the templates."


  def add_arguments(self, parser):
    super(Command, self).add_arguments(parser)
    parser.add_argument('--extra-gettext-option', default=[], dest='extra_gettext_option', action='append', help="Add an additional option to be passed to gettext. Ex: --extra-gettext-option='--keyword=mytrans'")
    


  def handle(self, *args, **options):
    # ensure that we have the necessary version of django
    if django_version[0] + django_version[1]/10 <= 1.7:
      raise CommandError('The dmp_makemessages command requires Django 1.8+ (the rest of DMP will work fine - this message is just for dmp_makemessages).')
    
    # go through each dmp_enabled app and compile its mako templates
    for app_name in _get_dmp_apps():
      self.compile_mako_files(app_name)
      
    # add any extra xgettext_options (the regular makemessages doesn't do this, and I need to include other aliases like _(), _z(), etc.
    for opt in options.get('extra_gettext_option', []):
      self.xgettext_options.append(opt)
    
    # call the superclass command
    return super(Command, self).handle(*args, **options)
    
    
  def compile_mako_files(self, app_name):
    '''Compiles the Mako templates within the apps of this system'''
    # import the module
    mod = import_module(app_name)
    
    # go through the files in the templates, scripts, and styles directories
    moddir = os.path.dirname(mod.__file__)
    for subdir_name, renderer in ( 
      ( 'templates', MakoTemplateRenderer(app_name) ),
      ( 'scripts', MakoTemplateRenderer(app_name, template_subdir="scripts") ),
      ( 'styles', MakoTemplateRenderer(app_name, template_subdir="styles") ),
    ):
      subdir = os.path.join(moddir, subdir_name)
      if os.path.exists(subdir):
        for filename in os.listdir(subdir):
          fname, ext = os.path.splitext(filename)
          if ext.lower() in ( '.htm', '.html', '.jsm', '.cssm' ):
            # create the template object, which creates the compiled .py file
            renderer.get_template(filename)
            
    