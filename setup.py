#!/usr/bin/env python3
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import io
import os
import re
from configparser import ConfigParser

from setuptools import find_packages, setup


def read(fname):
    content = io.open(
        os.path.join(os.path.dirname(__file__), fname),
        'r', encoding='utf-8').read()
    content = re.sub(
        r'(?m)^\.\. toctree::\r?\n((^$|^\s.*$)\r?\n)*', '', content)
    return content


def get_require_version(name):
    if minor_version % 2:
        require = '%s >= %s.%s.dev0, < %s.%s'
    else:
        require = '%s >= %s.%s, < %s.%s'
    require %= (name, major_version, minor_version,
        major_version, minor_version + 1)
    return require


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.pyc'):
                continue
            path2 = path.split(directory)
            paths.append(os.path.join(path2[1], filename))
    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! %s" % path2)
    # print(paths)
    return paths


config = ConfigParser()
config.read_file(open(os.path.join(os.path.dirname(__file__), 'tryton.cfg')))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
version = info.get('version', '0.0.1')
major_version, minor_version, _ = version.split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)
name = 'trytond_tinta'

download_url = 'http://downloads.tryton.org/%s.%s/' % (
    major_version, minor_version)
if minor_version % 2:
    version = '%s.%s.dev0' % (major_version, minor_version)
    download_url = (
        'hg+http://hg.tryton.org/modules/%s#egg=%s-%s' % (
            name[8:], name, version))

local_version = []
if os.environ.get('CI_JOB_ID'):
    local_version.append(os.environ['CI_JOB_ID'])
else:
    for build in ['CI_BUILD_NUMBER', 'CI_JOB_NUMBER']:
        if os.environ.get(build):
            local_version.append(os.environ[build])
        else:
            local_version = []
            break
if local_version:
    version += '+' + '.'.join(local_version)
requires = ['flask_tryton', 'flask', 'flask_babel']
for dep in info.get('depends', []):
    if not re.match(r'(ir|res)(\W|$)', dep):
        requires.append(get_require_version('trytond_%s' % dep))
requires.append(get_require_version('trytond'))

tests_require = []
dependency_links = []
if minor_version % 2:
    dependency_links.append(
        'https://trydevpi.tryton.org/?local_version='
        + '.'.join(local_version)
        )

setup(name=name,
    version=version,
    description='Random word generator for a drawing group.',
    long_description=read('README.rst'),
    author='Blaž Bregar',
    author_email='blaz@aklaro.si',
    url='https://www.aklaro.si/',
    download_url=download_url,
    project_urls={
        "Bug Tracker": 'https://bugs.tryton.org/',
        "Documentation": 'https://docs.tryton.org/projects/modules-tinta',
        "Forum": 'https://www.tryton.org/forum',
        "Source Code": 'https://hg.tryton.org/modules/tinta',
        },
    keywords='tinta trytond drawing',
    package_dir={
        'trytond.modules.tinta': '.',
        'tinta_flask': 'tinta_flask',
        },
    packages=(
        ['trytond.modules.tinta']
        + ['trytond.modules.tinta.%s' % p
            for p in find_packages()]
        + ['tinta_flask']
        + ['tinta_flask.tinta']
        + ['tinta_flask.tinta.%s' % p
            for p in find_packages('tinta_flask/tinta')]
        ),
    package_data={
        'trytond.modules.tinta': (info.get('xml', [])
            + ['tryton.cfg', 'view/*.xml', 'locale/*.po', '*.fodt',
                'icons/*.svg', 'tests/*.rst', 'templates/*.html']),
        'tinta_flask.tinta': (package_files('tinta_flask/tinta/')
            + ['templates/*.html', 'static/*', 'translations/**']),
        },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Artists',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Natural Language :: Slovenian',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Art',
        ],
    license='GPL-3',
    python_requires='>=3.7',
    install_requires=requires,
    extras_require={
        'test': tests_require,
        },
    dependency_links=dependency_links,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    tinta = trytond.modules.tinta
    """,  # noqa: E501
    )
