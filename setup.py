#!/usr/bin/env python
#encoding: utf-8
import os
import snorky

from setuptools import setup, find_packages

project_dir = os.path.dirname(__file__)

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(project_dir, *paths), 'r') as f:
        return f.read()

setup(
    name='snorky',
    version=snorky.version,
    description='Framework for developing WebSocket servers',
    url='http://snorkyproject.org',
    long_description=read('README.rst'),
    author='Juan Luis Boya García',
    author_email='ntrrgc@gmail.com',
    packages=find_packages(),
    install_requires=[
        "tornado<5.0",
        "requests",
        "funcsigs",
        "python-dateutil",
        "streql",
    ],
    tests_require=["mock"],
    include_package_data=False,
    license='MPL 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
