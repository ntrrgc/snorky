#!/usr/bin/env python3
import os
import re
import snorky
from subprocess import call
from shlex import split as sh

new_version = snorky.version

index = os.path.join(os.path.dirname(__file__), 'index.rst')
text = open(index).read()
cur_version = re.search('Download version (.*?):', text).groups()[0]

if new_version != cur_version:
    new_text = text.replace(cur_version, new_version)
    open(index, 'w').write(new_text)

    call(sh('git add') + [index])
    call(sh('git commit -m') + ['Documentation version bump'])
