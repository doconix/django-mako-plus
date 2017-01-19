from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import django_mako_plus

import os, os.path
from importlib import import_module


class Command(BaseCommand):
    args = '<name>'
    help = 'Creates a new Django-Mako-Plus app.'
    can_import_settings = True
    missing_args_message = "You must provide an application name."


    def add_arguments(self, parser):
        # required argument for the app name
        parser.add_argument('appname', type=str, help='the name of the new app')


    def handle(self, *args, **options):
        self.stdout.write("Error:")
        self.stdout.write('')
        self.stdout.write("As of v1.7, Django-Mako-Plus apps are creted with the standard Django command.")
        self.stdout.write("Please see https://github.com/doconix/django-mako-plus#create-a-dmp-style-app")
        self.stdout.write('')
        self.stdout.write("\t\t\t\t-- The Management")

