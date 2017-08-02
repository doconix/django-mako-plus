#!/usr/bin/env python

# This starts a web server on http://localhost:5500/ where doc files are automatically recompiled.
#
# If you need to create the docs from scratch, run:
# cd docs
# make html
#

from livereload import Server, shell
server = Server()
server.watch('docs/*.rst', shell('make html  --always-make', cwd='docs'))
server.watch('docs/_static/*.css', shell('make html  --always-make', cwd='docs'))
print('PORT IS 5500')
server.serve(root='docs/_build/html')