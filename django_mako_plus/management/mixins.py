import os, os.path



#########################################
###  Mixin for all DMP commands

class DMPCommandMixIn(object):
    '''Some extra SWAG that all DMP commands get'''

    def add_arguments(self, parser):
        super().add_arguments(parser)

        # django also provides a verbosity parameter
        # these two are just convenience params to it
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='Set verbosity to level 3 (see --verbosity).',
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Set verbosity to level 0, which silences all messages (see --verbosity).',
        )


    def get_action_by_dest(self, parser, dest):
        '''Retrieves the given parser action object by its dest= attribute'''
        for action in parser._actions:
            if action.dest == dest:
                return action
        return None


    def execute(self, *args, **options):
        '''Placing this in execute because then subclass handle() don't have to call super'''
        if options['verbose']:
            options['verbosity'] = 3
        if options['quiet']:
            options['verbosity'] = 0
        self.verbosity = options.get('verbosity', 1)
        super().execute(*args, **options)


    def get_dmp_path(self):
        '''Returns the absolute path to DMP.  Apps do not have to be loaded yet'''
        return os.path.dirname(os.path.dirname(__file__))


    def message(self, msg='', level=1, tab=0):
        '''Print a message to the console'''
        if self.verbosity >= level:
            self.stdout.write('{}{}'.format('    ' * tab, msg))
