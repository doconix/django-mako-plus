from django import VERSION as DJANGO_VERSION
from django.apps import apps
from django.core.management import BaseCommand
from django.core.management.base import CommandParser
from django_mako_plus.management.mixins import DMPCommandMixIn

from importlib import import_module
import os
import os.path
import sys
import pkgutil



SUBCOMMAND_DEST = 'subcommand'

class Command(DMPCommandMixIn, BaseCommand):
    '''Runs DMP subcommands'''
    help = "The dmp management command runs a number of subcommands.  See below for the available subcommands."
    requires_system_checks = False
    leave_locale_alone = True

    def __init__(self, *args, **kwargs):
        self.saved_args = args
        self.saved_kwargs = kwargs
        self.parser = None
        super().__init__(*args, **kwargs)


    def add_arguments(self, parser):
        super().add_arguments(parser)
        self.parser = parser

        # add each subcommand
        dmp_subparser = parser.add_subparsers(
            title='DMP subcommands: (`python3 manage.py dmp [subcommand] --help` for docs)',
            dest=SUBCOMMAND_DEST,
            metavar='',
        )
        for name in self.find_subcommands():
            current_subcommand = self.fetch_subcommand(name)
            kwargs = {}
            kwargs['description'] = current_subcommand.help
            kwargs['help'] = current_subcommand.help
            kwargs['add_help'] = False
            # this gets all the options from the subcommand into this command
            kwargs['parents'] = [ current_subcommand.create_parser('', '') ]
            if DJANGO_VERSION < ( 2, 1 ):
                kwargs['cmd'] = current_subcommand
            else:
                kwargs['called_from_command_line'] = parser.called_from_command_line
                kwargs['missing_args_message'] = parser.missing_args_message
            dmp_subparser.add_parser(name, **kwargs)


    def find_subcommands(self):
        # this is ripped from django.core.management.__init__.py (but uses 'subcommands')
        subcmd_dir = os.path.join(self.get_dmp_path(), 'management', 'subcommands')
        return [name for _, name, is_pkg in pkgutil.iter_modules([subcmd_dir])
                if not is_pkg and not name.startswith('_')]


    def fetch_subcommand(self, subcommand):
        mod = import_module('django_mako_plus.management.subcommands.{}'.format(subcommand))
        cmd = mod.Command(*self.saved_args, **self.saved_kwargs)
        cmd._called_from_command_line = self._called_from_command_line
        return cmd


    def handle(self, *args, **options):
        # the dmp_command is required (not sure how to set this in the arguments above?)
        if not options[SUBCOMMAND_DEST]:
            self.print_help('', self.parser.prog)
            return

        # trigger the subcommand handling
        subcommand = self.fetch_subcommand(options[SUBCOMMAND_DEST])
#        subcommand.requires_system_checks = self.requires_system_checks
        subcommand.execute(*args, **options)
