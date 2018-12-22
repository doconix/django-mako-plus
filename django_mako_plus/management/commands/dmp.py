from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django_mako_plus.management.mixins import DMPCommandMixIn

import os, os.path, shutil
import sys
import argparse

# this command was placed here in Sept 2018 to help users know about the change.
# it can probably be removed sometime in Summer, 2019.


class Command(DMPCommandMixIn, BaseCommand):
    help = 'Message to inform users of the change back to dmp_* commands.'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(dest='all', nargs=argparse.REMAINDER, help='Wildcard to catch all remaining arguments')

    def handle(self, *args, **options):
        try:
            pos = sys.argv.index('dmp')  # should be 1
            guess = 'Our guess at the right command is:\n\n    {}'.format(' '.join(
                sys.argv[:pos] + \
                [ sys.argv[pos] + '_' + sys.argv[pos+1] ] + \
                sys.argv[pos+2:]
            ))
        except:  # `dmp` not there, or no subcommand
            guess = ''
        raise CommandError('''

DMP command usage changed in v5.6: `manage.py dmp *` commands are now `manage.py dmp_*`.

As much as we liked the former syntax, it had to be tied to Django internals. It broke
whenever Django changed its internal command structure. Apologies for the change.

{}
        '''.format(guess))
