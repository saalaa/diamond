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
