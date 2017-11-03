from django_mako_plus import uid



class Tester(uid.Tester):
    # extending it here allows the Django test suite to find
    # the tests already in the uid module
    pass
