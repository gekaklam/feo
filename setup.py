#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Jakob Luettgau
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# This file mostly metadata to describe this python package.

import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# package metadata
config = {
    'name': 'feo-tape-library-simulation',
    'version': '0.1',
    #'packages': ['tapesim'],
    'packages': find_packages(),
    'description': 'A tape library simulation',
    'author': 'Jakob Luettgau',
    'url': 'https://github.com/jakobluettgau/feo',
    'download_url': '',
    'author_email': 'luettgau@dkrz.de',
    'install_requires': ['nose'],
    'scripts': [],
    'zip_safe': False,
}

setup(**config)
