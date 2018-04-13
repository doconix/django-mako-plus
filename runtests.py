#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    os.chdir('./tests_project')
    sys.path.insert(0, os.getcwd())
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests_project.settings'
    import django
    django.setup()
    from django.conf import settings
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(sys.argv[1:])
    print()
    print('Note: some of the tests produce exceptions and stack traces in the output, but these are the expected exceptions resulting from tests.  Focus on whether the tests ran without failures (not on the expected exceptions).')
    print()
    sys.exit(bool(failures))
