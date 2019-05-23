#!/usr/bin/env python

from distutils.core import setup

kwargs = {
	'name': 'pyicub',
	'version': '0.1',
        'packages': ['pyicub'],
#        'package_dir': {'': 'pyicub'},
	'description': 'Python iCub wrapper',
        'author': 'Davide De Tommaso',
        'author_email': 'davide.detommaso@iit.it',
        'url': 'https://github.com/s4hri/pyicub',
        'license': 'GPLv3'
}


setup(**kwargs)

