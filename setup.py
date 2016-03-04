import os, os.path, sys
from distutils.core import setup

MODULE_NAME = 'django_mako_plus'

VERSION = __import__(MODULE_NAME).__version__
CLASSIFIERS = [
  'Framework :: Django',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: Apache Software License',
  'Operating System :: OS Independent',
  'Topic :: Software Development',
]
install_requires = [
  'django>=1.4.1',
  'mako>=0.9.0',
]

# Compile the list of packages available
packages = []
def walk(root):
  for fname in os.listdir(root):
    fpath = os.path.join(root, fname)
    # skip hidden/cache files
    if fname.startswith('.') or fname in ( '__pycache__', ):
      continue
    # if a directory, walk it
    elif os.path.isdir(fpath):
      walk(fpath)
    # if an __init__.py file, add the directory to the packages
    elif fname == '__init__.py':
      packages.append(os.path.dirname(fpath))
walk(MODULE_NAME)

# add the app_template directory to data files
# empty directories within app_template/ will cause problems with distutils, so be sure each directory has at least one file
data_files = []
# add the readme/license
data_files.extend([
  ('', [ 'readme.md' ]),
  ('', [ 'readme.txt' ]),
  ('', [ 'license.txt' ]),
])

# add the app_template/ directory
package_data_files = []
app_template_dir = 'controller/app_template'
for root, dirs, files in os.walk(os.path.join(MODULE_NAME, app_template_dir)):
  for fname in files:
    if fname.startswith('.') or fname in ( '__pycache__', ): # skip hidden/cache files
      continue
    package_data_files.append(os.path.join(root[len(MODULE_NAME)+1:], fname))
    
# read the long description if sdist
description = 'Combines Django framework and Mako templating engine, plus a few bonuses.'
long_description = description
if sys.argv[1] == 'sdist':
  long_description = open('readme.txt').read()

# run the setup
setup(
  name=MODULE_NAME,
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
#  install_requires=install_requires,
  classifiers=CLASSIFIERS,
  license='Apache 2.0',
)