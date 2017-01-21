import os, os.path, sys
from setuptools import setup

MODULE_NAME = 'django_mako_plus'


# I can't import the version file the normal way because it loads
# __init__.py, which then imports the DMP engine.  Thanks to sorin
# on StackOverflow for this idea.
exec(open('django_mako_plus/version.py').read())
VERSION = __version__

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python :: 3 :: Only',
    'Framework :: Django',
    'Framework :: Django :: 1.10',
    'Framework :: Django :: 1.4',
    'Framework :: Django :: 1.5',
    'Framework :: Django :: 1.6',
    'Framework :: Django :: 1.7',
    'Framework :: Django :: 1.8',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
]
install_requires = [
    'django >= 1.8.0',
    'mako >= 1.0.0',
]

# remove the __pycache__ directories since the ones in project_template seems to stick around
os.system('find . -name "__pycache__" -type d -exec rm -r "{}" \; > /dev/null')

# Compile the list of packages available
packages = []
def walk(root):
  for fname in os.listdir(root):
    fpath = os.path.join(root, fname)
    # skip hidden/cache files
    if fname.startswith('.') or fname.endswith('.pyc') or fname in ( '__pycache__', 'app_template', 'project_template' ):
      continue
    # if a directory, walk it
    elif os.path.isdir(fpath):
      walk(fpath)
    # if an __init__.py file, add the directory to the packages
    elif fname == '__init__.py':
      packages.append(os.path.dirname(fpath))
walk(MODULE_NAME)

data_files = []
# add the readme/license
data_files.extend([
    ('', [ 'readme.md' ]),
    ('', [ 'readme.txt' ]),
    ('', [ 'license.txt' ]),
])

# add the app_template/ and package_template/ directory
# empty directories within app_template/ will cause problems with distutils, so be sure each directory has at least one file
package_data_files = []
for template_dir in ( 'app_template', 'project_template' ):
    for root, dirs, files in os.walk(os.path.join(MODULE_NAME, template_dir)):
      dirs[:] = [ d for d in dirs if not d.startswith('.') and not d in ( '__pycache__', ) ] # skip hidden and __pycache__ directories
      for fname in files:
        if fname.startswith('.') or fname.endswith('.pyc'): # skip hidden/cache files
          continue
        package_data_files.append(os.path.join(root[len(MODULE_NAME)+1:], fname))

# read the long description if sdist
description = 'Django+Mako: Advanced, mature connector for Mako templates'
long_description = description
if len(sys.argv) > 1 and sys.argv[1] == 'sdist':
  long_description = open('readme.txt').read()

# run the setup
setup(
  name='django-mako-plus',
  description=description,
  long_description=long_description,
  version=VERSION,
  author='Conan Albrecht',
  author_email='ca@byu.edu',
  url="https://github.com/doconix/django-mako-plus",
  download_url="https://github.com/doconix/django-mako-plus/archive/master.zip",
#  package_dir={ MODULE_NAME: MODULE_NAME },
  packages=packages,
  package_data = {
    MODULE_NAME: package_data_files,
  },
#  data_files=data_files,
  install_requires=install_requires,
  classifiers=CLASSIFIERS,
  license='Apache 2.0',
)
