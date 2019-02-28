#!/usr/bin/env python3

from django_mako_plus.version import __version__
from django_mako_plus.command import run_command

import sys
import os
import re
import shutil
import json


# set the version number in package.json
print('Updating the version in package.json...')
PACKAGE_JSON = 'django_mako_plus/webroot/package.json'
with open(PACKAGE_JSON) as fin:
    data = json.load(fin)
data['version'] = __version__
with open(PACKAGE_JSON, 'w') as fout:
    json.dump(data, fout, sort_keys=True, indent=4)

# set the version number in dmp-common.src.js
print('Updating the version in JS...')
VERSION_PATTERN = re.compile("__version__\ = '\w+\.\w+\.\w+'")
DMP_COMMON = 'django_mako_plus/webroot/dmp-common.src.js'
with open(DMP_COMMON) as fin:
    content = fin.read()
match = VERSION_PATTERN.search(content)
if not match:
    raise RuntimeError('Version pattern did not match.  Aborting because the version number cannot be updated in dmp-common.src.js.')
content = VERSION_PATTERN.sub("__version__ = '{}'".format(__version__), content)
with open(DMP_COMMON, 'w') as fout:
    fout.write(content)

# backport and minify dmp-common.src.js
print('Backporting and minifying JS...')
run_command('npm', 'run', 'build', cwd='./django_mako_plus/webroot/')

# update the archives
print('Creating the archives...')
shutil.make_archive('app_template', 'zip', root_dir='./django_mako_plus/app_template')
shutil.make_archive('project_template', 'zip', root_dir='./django_mako_plus/project_template')

# make the documentation, since GitHub Pages reads it as static HTML
print('Making the documentation...')
run_command('make', 'html', cwd='./docs-src')

# run the setup and upload
print()
if input('Ready to upload to PyPi. Continue? ')[:1].lower() == 'y':
    ret = run_command('python3', 'setup.py', 'sdist')
    print(ret.stdout)
    ret = run_command('twine', 'upload', 'dist/*')
    print(ret.stdout)
    run_command('rm', '-rf', 'dist/', 'django_mako_plus.egg-info/')

    ret = run_command('npm', 'publish', cwd='./django_mako_plus/webroot/')
    print(ret.stdout)
