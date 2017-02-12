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
    name='diamond-wiki',
    version=version('diamond/__init__.py'),
    url='https://github.com/saalaa/diamond',
    license='GPL',
    author='Benoit Myard',
    author_email='myardbenoit@gmail.com',
    description='The metadata enabled wiki engine',
    long_description='See https://github.com/saalaa/diamond',
    zip_safe=False,
    include_package_data=True,
    packages=['diamond'],
    install_requires=requirements('requirements.txt'),
    setup_requires=['pytest-runner'],
    tests_requires=['pytest-runner'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Office/Business :: Groupware',
        'Topic :: Text Processing :: Markup'
    ],
    entry_points={
        'console_scripts': [
            'diamond = diamond.main:main'
        ]
    }
)
