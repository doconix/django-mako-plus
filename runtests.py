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
    sys.exit(bool(failures))

