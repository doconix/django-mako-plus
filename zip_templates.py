#!/usr/bin/env python
'''
Regenerates the zip files of the app_template/ and project_template/ directories.
These must be in zip files for startproject and startapp to pull them from the
GitHub site.
'''

import os, shutil

shutil.make_archive('app_template', 'zip', root_dir='./django_mako_plus/app_template')
shutil.make_archive('project_template', 'zip', root_dir='./django_mako_plus/project_template')


