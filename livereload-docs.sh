#!/usr/bin/env python
from livereload import Server, shell
server = Server()
server.watch('docs/*.rst', shell('make html ', cwd='docs'))
server.watch('docs/_static/*.css', shell('make html ', cwd='docs'))
print('PORT IS 5500')
server.serve(root='docs/_build/html')