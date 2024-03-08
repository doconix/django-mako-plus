#!/usr/bin/env python3
from django.core import management
import os.path
import sys
import functools

__doc__ = '''
Starts a new DMP-style project.  This is the DMP equivalent of "django-admin.py startproject".

Example:

    django_mako_plus dmp_startproject [project name]

if the above doesn't work, try:

    python -m django_mako_plus dmp_startproject [project name]

Background: The dmp_startproject command has a bit of a chicken-and-egg problem.
It creates the project, but the command isn't available until the project is created
and DMP is in INSTALLED_APPS.  Can't create until it is created...
Django solves this with django-admin.py, a global Python script that can be
executed directly from the command line.
'''

DMP_MANAGEMENT_PATH = os.path.join(os.path.dirname(__file__), 'management')



def main():
    # Django is hard coded to return only its own commands when a project doesn't
    # exist yet.  Since I want DMP to be able to create projects, I'm monkey-patching
    # Django's get_commands() function so DMP gets added.  This is the least-offensive
    # way I could see to do this since Django really isn't built to allow other commands
    # pre-project.  This only happens when `django_mako_plus` is run directly and not
    # when `manage.py` or `django-admin.py` are run.
    orig_get_commands = management.get_commands
    @functools.lru_cache(maxsize=None)
    def new_get_commands():
        commands = {}
        commands.update(orig_get_commands())
        commands.update({ name: 'django_mako_plus' for name in management.find_commands(DMP_MANAGEMENT_PATH) })
        return commands
    management.get_commands = new_get_commands

    # mimic the code in django-admin.py
    management.execute_from_command_line()


## runner!
if __name__ == '__main__':
    main()
