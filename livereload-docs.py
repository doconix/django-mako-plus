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
class Runner:
    def __init__(self, cmd, cwd):
        self.cmd = cmd
        self.cwd = cwd
    def __str__(self):
        return ' '.join(self.cmd)
    def __call__(self):
        p = Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=self.cwd, shell=False)
        stdout, stderr = p.communicate()
        if stderr:
            logger.error('\n' + stderr.decode())
            return stderr
        if stdout:
            logger.info('\n' + stdout.decode())
            return stdout

server = Server()
server.watch('docs/*.rst', Runner(['make', 'html', '--always-make' ], cwd='docs'))
server.watch('docs/_static/*.css', Runner(['make', 'html', '--always-make' ], cwd='docs'))
print('PORT IS 5500')
server.serve(root='docs/_build/html/', restart_delay=1)
