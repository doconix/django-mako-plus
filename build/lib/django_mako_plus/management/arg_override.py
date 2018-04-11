class ArgumentOverrideMixIn(object):
    '''
    A mixin that allows overriding of arguments in Django Commands

    Example:
        class Command(ArgumentOverrideMixIn, ExistingCommand):
            def customize_somedest(self, action):
                """Allows overriding the dest="somedest" argument"""
                action.default = 'some default value'
                action.choices = ...

    '''

    def add_arguments(self, parser):
        # let the super add the arguments
        super().add_arguments(parser)

        ## Note that I'm accessing the internal parser._actions list because
        ## argparse gives no way to access the arguments added by the our super.
        ## The other option is to add the arguments ourselves and not call the super.
        ## I think this is the least offensive way to do it, but I'm open to suggestions.
        for action in parser._actions:
            mthd = getattr(self, 'customize_' + action.dest, None)
            if mthd is not None:
                mthd(action)

    # def customize_somedest(self, action):
    #     '''Allows customization of an action.  `somedest` should be the dest= name of the arg.'''
    #     action.default = 'some default value'
    #     action.choices = ...
