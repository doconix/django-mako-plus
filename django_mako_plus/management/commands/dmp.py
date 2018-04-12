from django.core.management import BaseCommand
from django.core.management.base import CommandParser
from django_mako_plus.util import get_dmp_path
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
    # settings might not be available yet, so can't set locale or run checks
    # once a subcommand is selected, these are reset to the subcommand settings
    leave_locale_alone = True
    requires_system_checks = False

    def __init__(self, *args, **kwargs):
        self.saved_args = args
        self.saved_kwargs = kwargs
        self.parser = None
        super().__init__(*args, **kwargs)


    def fetch_subcommand(self, subcommand):
        mod = import_module('django_mako_plus.management.subcommands.{}'.format(subcommand))
        cmd = mod.Command(*self.saved_args, **self.saved_kwargs)
        cmd._called_from_command_line = self._called_from_command_line
        return cmd


    def add_arguments(self, parser):
        super().add_arguments(parser)
        self.parser = parser

        # add a subparser for each subcommand
        current_subcommand = None
        def create_subparser(**kwargs):
            # I have to ask Django to create the parser and then use that as
            # a parent (template) for a new parser because django doesn't allow
            # the extra args and kwargs in its factory method (lame).
            kwargs['parents'] = [ current_subcommand.create_parser('', '') ]
            return CommandParser(current_subcommand, **kwargs)
        subparsers = parser.add_subparsers(
            title='DMP subcommands: (`python3 manage.py dmp [subcommand] --help` for docs)',
            dest=SUBCOMMAND_DEST,
            metavar='',
            parser_class=create_subparser,
        )
        for name in find_subcommands():
            current_subcommand = self.fetch_subcommand(name)
            subparsers.add_parser(name, description=current_subcommand.help, help=current_subcommand.help, add_help=False)


    def handle(self, *args, **options):
        # the dmp_command is required (not sure how to set this in the arguments above?)
        if not options[SUBCOMMAND_DEST]:
            self.print_help('', self.parser.prog)
            return

        # trigger the subcommand handling
        subcommand = self.fetch_subcommand(options[SUBCOMMAND_DEST])
        self.leave_locale_alone = subcommand.leave_locale_alone
        self.requires_system_checks = subcommand.requires_system_checks
        subcommand.execute(*args, **options)



#########################################
###   Helper functions

def find_subcommands():
    # this is ripped from django.core.management.__init__.py and switched to our subcommand dir
    command_dir = os.path.join(get_dmp_path(), 'management', 'subcommands')
    return [name for _, name, is_pkg in pkgutil.iter_modules([command_dir])
            if not is_pkg and not name.startswith('_')]
