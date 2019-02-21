import os, os.path, sys, re
from fnmatch import fnmatch
from setuptools import setup

MODULE_NAME = 'django_mako_plus'

IGNORE_PATTERNS = [
    '.*',
    '__pycache__',
    '*.pyc',
    '__dmpcache__',
    'node_modules',
    '.vscode',
    '.DS_Store',
]
def is_ignore(fn):
    for pat in IGNORE_PATTERNS:
        if fnmatch(fn, pat):
            return True
    return False

# I can't import the version file the normal way because it loads
# __init__.py, which then imports the DMP engine.
with open('django_mako_plus/version.py') as f:
    match = re.search("__version__\s=\s'(\d+\.\d+\.\d+)'", f.read())
    if not match:
        print('Cannot determine the DMP version. Aborting setup.py.')
        sys.exit(1)
    VERSION = match.group(1)


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python :: 3 :: Only',
    'Framework :: Django',
    'Framework :: Django :: 1.11',
    'Framework :: Django :: 1.10',
    'Framework :: Django :: 1.9',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
]
install_requires = [
    'django >= 1.9.0',
    'mako >= 1.0.0',
]


if len(sys.argv) >= 2 and sys.argv[1] == 'sdist':
    # remove the __pycache__ directories since the ones in project_template seems to stick around
    os.system('find . -name "__pycache__" -type d -exec rm -r "{}" \+')

# Compile the list of packages available
packages = []
def walk(parent):
    for fname in os.listdir(parent):
        fpath = os.path.join(parent, fname)
        # skip hidden/cache files
        if is_ignore(fname) or fname in ( 'app_template', 'project_template' ):
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

# add the extra directories
# empty directories within app_template/ will cause problems with distutils, so be sure each directory has at least one file
package_data_files = []
def walk2(parent):
    for fname in os.listdir(parent):
        fpath = os.path.join(parent, fname)
        if is_ignore(fname):
            pass  # ignore this one
        elif os.path.isdir(fpath):
            walk2(fpath)
        else:
            package_data_files.append(os.path.relpath(fpath, MODULE_NAME))
walk2(os.path.join(MODULE_NAME, 'app_template'))
walk2(os.path.join(MODULE_NAME, 'project_template'))
walk2(os.path.join(MODULE_NAME, 'webroot'))

# read the long description if sdist
description = 'Django+Mako: Routing by Convention, Python-Centric Template Language'
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
  author_email='doconix@gmail.com',
  url="http://django-mako-plus.readthedocs.io/",
  download_url="https://github.com/doconix/django-mako-plus/archive/master.zip",
  packages=packages,
  package_data = {
    MODULE_NAME: package_data_files,
  },
  entry_points={
    'console_scripts': [
      'django_mako_plus = django_mako_plus.__main__:main'
    ]
  },
  install_requires=install_requires,
  classifiers=CLASSIFIERS,
  license='Apache 2.0',
)
