#!/usr/bin/env python3
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    if len(sys.argv) == 1:
        args = [ 'tests' ]
    else:
        args = sys.argv[1:]
    failures = test_runner.run_tests(args)
    print()
    print('Note: some of the tests produce exceptions and stack traces in the output, but these are the expected exceptions resulting from tests.  Focus on whether the tests ran without failures (not on the expected exceptions).')
    print()
    sys.exit(bool(failures))

