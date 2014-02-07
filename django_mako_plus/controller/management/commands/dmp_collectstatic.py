from django.core.management.base import BaseCommand, CommandError
from django.utils.importlib import import_module
from django.conf import settings
from django_mako_plus.controller import router
from optparse import make_option
import os, os.path, shutil
try:
  from rjsmin import jsmin
  JSMIN = True
except ImportError:
  JSMIN = False
try:
  from rcssmin import cssmin
  CSSMIN = True
except ImportError:
  CSSMIN = False


class Command(BaseCommand):
  args = ''
  help = 'Collects static files, such as media, scripts, and styles, to a common directory root. This is done to prepare for deployment.  If the rjsmin and/or rcssmin modules are available, *.js and *.css files are minified during collection.'
  can_import_settings = True
  option_list = BaseCommand.option_list + (
          make_option(
            '--overwrite', 
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrite existing files in the directory when necessary.'
          ),
          make_option(
            '--no-minify', 
            action='store_true',
            dest='nominify',
            default=False,
            help='Do not minify *.js and *.css files when they are found.'
          ),
  )# option_list
  
  
  def handle(self, *args, **options):
    # save the options for later
    self.options = options
    
    # ensure we have a base directory
    try:
      if not os.path.isdir(os.path.abspath(settings.BASE_DIR)):
        raise CommandError('Your settings.py BASE_DIR setting is not a valid directory.  Please check your settings.py file for the BASE_DIR variable.')
    except AttributeError as e:
      print(e)
      raise CommandError('Your settings.py file is missing the BASE_DIR setting. Aborting app creation.')
    
    # get the destination directory, and ensure it doesn't already exist
    # if dest_root starts with a /, it is an absolute directory
    # if dest_root doesn't start with a /, it goes relative to the BASE_DIR
    try:
      dest_root = os.path.join(os.path.abspath(settings.BASE_DIR), settings.STATIC_ROOT)
      if os.path.exists(dest_root) and not self.options['overwrite']:
        raise CommandError('The destination directory for static files (%s) already exists. Please delete it or run this command with the --overwrite option.' % dest_root)
    except AttributeError:
      raise CommandError('Your settings.py file is missing the STATIC_ROOT setting. Exiting without collecting the static files.')
      
    # create the directory - we assume it either doesn't exist, or the --overwrite is specified
    if not os.path.isdir(dest_root):
      os.makedirs(dest_root)

    # go through the DMP apps and collect the static files
    for appname in router.TEMPLATE_RENDERERS:  # this map holds the DMP-enabled apps
      try:
        module_obj = import_module(appname)
      except ImportError as e:
        raise CommandError('Could not import app %s: %s' % (appname, e))
      app_root = os.path.abspath(os.path.dirname(module_obj.__file__))
      self.copy_dir(app_root, dest_root)
    
    # tell the user we're done
    self.stdout.write("Your static files have been successfully copyied into %s" % dest_root)
    
    
    
  def copy_dir(self, source, dest, level=0):
    '''Copies the static files from one directory to another.  If this command is run, we assume the user wants to overwrite any existing files.'''
    for fname in os.listdir(source):
      source_path = os.path.join(source, fname)
      dest_path = os.path.join(dest, fname)
      ext = os.path.splitext(fname)[1].lower()
    
      ###  DIRECTORIES FIRST  ###
      # ignore these directories
      if os.path.isdir(source_path) and fname in ( 'templates', 'views', settings.MAKO_TEMPLATES_CACHE_DIR, '__pycache__' ):
        pass
        
      # if a directory, create it in the destination and recurse
      elif os.path.isdir(source_path):
        if not os.path.exists(dest_path):
          os.mkdir(dest_path)
        elif not os.path.isdir(dest_path):  # could be a file or link
          os.unlink(dest_path)
          os.mkdir(dest_path)
        self.copy_dir(source_path, dest_path, level+1)

      ###   FILES NEXT   ###
      # we don't do any regular files at the top level      
      elif level == 0:
        pass
        
      # ignore these files
      elif fname in ( '__init__.py', ):
        pass
      
      # ignore these extensions
      elif ext in ( '.cssm', '.jsm' ):
        pass
      
      # if a regular Javscript file, minify it
      elif ext == '.js' and JSMIN and self.options['nominify'] == False:
        fin = open(source_path)
        fout = open(dest_path, 'w')
        fout.write(jsmin(fin.read()))
        fout.close()
        fin.close()
      
      elif ext == '.css' and CSSMIN and self.options['nominify'] == False:
        fin = open(source_path)
        fout = open(dest_path, 'w')
        fout.write(cssmin(fin.read()))
        fout.close()
        fin.close()
      
      # if we get here, it's a binary file like an image, movie, pdf, etc.
      else:
        shutil.copy2(source_path, dest_path)
      
    
      
    