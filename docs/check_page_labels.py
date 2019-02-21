#!/usr/bin/env python3

import glob, os

for fname in glob.glob('*.rst'):
    with open(fname) as fin:
        contents = fin.read()
        if not contents.startswith('..  _'):
            print('{}: updating page label'.format(fname))
            with open(fname, 'w') as fout:
                fout.write('..  _{}:\n\n{}'.format(
                    os.path.splitext(fname)[0],
                    contents,
                ))
