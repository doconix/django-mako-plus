# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
# 	-E :: don't use a saved environment, always read all files
#   -a :: write all files (not just changed)
#   -q :: no stdout, just stderr
SPHINXOPTS    = -E -a -q
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = Django-Mako-Plus
SOURCEDIR     = .
BUILDDIR      = ../docs/

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

html: Makefile
	@python3 make_page_labels.py
	@$(SPHINXBUILD) "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@touch ${BUILDDIR}.nojekyll
