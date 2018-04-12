import sys



##############################################
###  Mixin for messages different verbosities

class MessageMixIn(object):
    '''
    A mixin that allows printing messages at
    different verbosities.  Similar to logging
    but much simpler.
    '''

    def add_arguments(self, parser):
        super().add_arguments(parser)

        # django also provides a verbosity parameter
        # these two are just convenience params to it
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='Set verbosity to level 3 (see --verbosity).'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='Set verbosity to level 0, which silences all messages (see --verbosity).'
        )


    def execute(self, *args, **options):
        # I'm overriding execute instead of handle because I want this
        # to come before handle(), even if this mix in is listed second.
        if options['verbose']:
            options['verbosity'] = 3
        if options['quiet']:
            options['verbosity'] = 0
        self.options = options
        super().execute(*args, **options)


    def message(self, msg='', level=1, tab=0):
        '''Print a message to the console'''
        # verbosity=1 is the default if not specified in the options
        if self.options['verbosity'] >= level:
            self.stdout.write('{}{}'.format('    ' * tab, msg))





##############################################
###  Mixin for overriding a Django command
###  using the same name.

class CommandOverrideMixIn(object):
    '''
    A mixin that asks the user whether to run the Django version
    or the DMP version of a command.

    This allows us to directly override a Django command using
    the exact same name.
    '''
    # subclasses should probably override these strings for more descriptive choices
    QUESTION = 'Which would you like to run?'
    CHOICE_DMP = 'DMP-specific command (default)'
    CHOICE_DJANGO = 'Standard Django command'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--dmp',
            action='store_false',
            dest='django_version',
            default=None,
            help='Run the DMP specialization of this command.'
        )
        parser.add_argument(
            '--django',
            action='store_true',
            dest='django_version',
            default=None,
            help='Run the normal Django version of this command.'
        )


    def get_argument_by_dest(self, parser, dest):
        '''Retrieves the argparse argument by the given dest string'''
        # I'm accessing the private field here because I don't see another way to
        # get at already-defined actions.  This method seems to be the least-offensive
        # way to code around it.
        for action in parser._actions:
            if action.dest == dest:
                return action
        return None


    def handle(self, *args, **options):
        '''Subclasses should override dmp_handle rather than this method'''
        # if needed, ask the user which version to run
        if options['django_version'] is None:
            print('Two versions of this command are available:')
            print()
            print('    1. {}'.format(self.CHOICE_DMP))
            print('    2. {}'.format(self.CHOICE_DJANGO))
            print('    3. Quit')
            print()
            print('(you can skip this question by specifying --dmp or --django)')
            print()
            while True:
                choice = input('{} '.format(self.QUESTION))
                choice = choice.strip()[:1]
                if choice == '1' or choice == '':
                    options['django_version'] = False
                    break
                elif choice == '2':
                    options['django_version'] = True
                    break
                elif choice == '3':
                    sys.exit(0)
                print('Please enter a choice number.')

        # call the appropriate handle method
        if options['django_version']:
            super().handle(*args, **options)
        else:
            self.dmp_handle(*args, **options)


    def dmp_handle(self, *args, **options):
        '''Subclasses should override this method for the DMP behavior'''
        print('dmp version')
