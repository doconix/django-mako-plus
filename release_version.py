#!/usr/bin/env python3

from django_mako_plus.version import __version__
from django_mako_plus.command import run_command

import sys, os, os.path, re, shutil
from rjsmin import jsmin


# set the version number in dmp-common.js
print('Updating the version in .js files...')
VERSION_PATTERN = re.compile("__version__\: '\w+\.\w+\.\w+'")
DMP_COMMON = 'django_mako_plus/webroot/dmp-common'
with open(DMP_COMMON + '.js') as f:
    content = f.read()
match = VERSION_PATTERN.search(content)
if not match:
    raise RuntimeError('Version pattern did not match.  Aborting because the version number cannot be updated in dmp-common.js.')
content = VERSION_PATTERN.sub("__version__: '{}'".format(__version__), content)
with open(DMP_COMMON + '.js', 'w') as f:
    f.write(content)
with open(DMP_COMMON + '.min.js', 'w') as f:
    f.write(jsmin(content))
    
# update the archives
print('Creating the archives...')
shutil.make_archive('app_template', 'zip', root_dir='./django_mako_plus/app_template')
shutil.make_archive('project_template', 'zip', root_dir='./django_mako_plus/project_template')
    
# run the setup and upload
print()
if input('Ready to upload to PyPi. Continue? ')[:1].lower() == 'y':
    ret = run_command('python3', 'setup.py', 'sdist')
    print(ret.stdout)
    ret = run_command('twine', 'upload', 'dist/*')
    print(ret.stdout)
    run_command('rm', '-rf', 'dist/', 'django_mako_plus.egg-info/')
