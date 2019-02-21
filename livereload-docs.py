#!/usr/bin/env python

# This starts a web server on http://localhost:5500/ where doc files are automatically recompiled.
#
# If you need to create the docs from scratch, run:
# cd docs
# make html
#

from livereload import Server
from subprocess import Popen, PIPE

# livereload's run_shell doesn't encode errors right (leaves them bytes)
import logging
logger = logging.getLogger('livereload')
def shell(cmd, cwd):
    def run_shell():
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd, shell=False)
        stdout, stderr = p.communicate()
        if stderr:
            logger.error('\n' + stderr.decode())
            return stderr
        if stdout:
            logger.info(stdout.decode())
    return run_shell

server = Server()
server.watch('docs/*.rst', shell(['make', 'html', '--always-make' ], cwd='docs'))
server.watch('docs/_static/*.css', shell(['make', 'html', '--always-make' ], cwd='docs'))
print('PORT IS 5500')
server.serve(root='docs/_build/html', restart_delay=1)
