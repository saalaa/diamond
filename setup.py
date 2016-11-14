# Copyright (C) 1999, 2000 Martin Pool <mbp@humbug.org.au>
# Copyright (C) 2003 Kimberley Burchett <http://www.kimbly.com>
# Copyright (C) 2016 Benoit Myard <myardbenoit@gmail.com>
#
# This file is part of Diamond wiki.
#
# Diamond wiki is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Diamond wiki is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Diamond wiki. If not, see <http://www.gnu.org/licenses/>.

import re

from setuptools import setup

VERSION_RE = re.compile(r"__version__ = '(.*)'")

def version(filename):
    with open(filename) as file:
        source = file.read()

        return VERSION_RE.search(source) \
                .group(1)

def requirements(filename):
    with open(filename) as file:
        return file.read() \
                .split()

setup(
    name='Diamond',
    version=version('diamond/__init__.py'),
    url='http://github.com/saalaa/diamond',
    license='GPL',
    author='Benoit Myard',
    author_email='myardbenoit@gmail.com',
    description='The metadata enabled wiki engine',
    install_requires=requirements('requirements.txt'),
    tests_require=requirements('requirements-test.txt'),
    setup_requires=['pytest-runner']
)
