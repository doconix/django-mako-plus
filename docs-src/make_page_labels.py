#!/usr/bin/env python3

import glob, os, re

EXISTING_RE = re.compile(r'^\.\.\s+_\w+:\n+')

for fname in glob.glob('*.rst'):
    with open(fname) as fin:
        contents = fin.read()
        prevcontents = contents
        label = '.. _{}:\n\n'.format(os.path.splitext(fname)[0])
        EXACT_RE = re.compile(r'^\.\. _{}:\n\n[^\n]'.format(os.path.splitext(fname)[0]))
        if not EXACT_RE.search(contents):
            if EXISTING_RE.search(contents):    # existing line is wrong, so replace
                contents = EXISTING_RE.sub(label, contents)
            else:                               # none there, so insert
                contents = label + contents
        if prevcontents != contents:
            print('Fixed label in {}'.format(fname))
            with open(fname, 'w') as fout:
                fout.write(''.join(contents))
