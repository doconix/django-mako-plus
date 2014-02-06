from django.core.management.base import BaseCommand, CommandError
from django.utils.importlib import import_module
from django.conf import settings
from django_mako_plus.controller import router
import os, os.path


class Command(BaseCommand):
  args = ''
  help = 'Collects static files, such as media, scripts, and styles, to a common directory root. This is done to prepare for deployment.'
  can_import_settings = True
  
  def handle(self, *args, **options):
    # ensure we have a base directory
    try:
      if not os.path.isdir(settings.BASE_DIR):
        raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
    except AttributeError:
      raise CommandError('Your settings.py file is missing the BASE_DIR setting. Aborting app creation.')
    
    # get the destination directory, and ensure it doesn't already exist
    # if STATIC_ROOT starts with a /, it is an absolute directory
    # if STATIC_ROOT doesn't start with a /, it goes relative to the BASE_DIR
    try:
      static_root = os.path.join(settings.BASE_DIR, settings.STATIC_ROOT)
      if os.path.exists(static_root):
        raise CommandError('The destination directory for static files (%s) already exists. Please delete it or run this command with the --overwrite options.' % static_root)
    except AttributeError:
      raise CommandError('Your settings.py file is missing the BASE_DIR setting. Aborting app creation.')
    
    # create the directory - we assume it either doesn't exist, or the --overwrite is specified
    if not os.path.isdir(settings.static_root):
      os.makedirs(settings.static_root)

    # go through the apps and collect the static files
    
    
    self.stdout.write("Your static files have been successfully copyied into %s" % static_root)
    
    
    
  def process_app(static_root, app_root):