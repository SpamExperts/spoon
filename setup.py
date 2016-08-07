#! /usr/bin/env python

from __future__ import absolute_import

import spoon
import distutils.core

REQUIRES = []
DESCRIPTION = """Simple to use pre-forking server interface."""

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
]

distutils.core.setup(
    name='spoon',
    description=DESCRIPTION,
    author="SpamExperts",
    version=spoon.__version__,
    license='GPL',
    platforms='POSIX',
    keywords='server',
    classifiers=CLASSIFIERS,
    # scripts=[],
    requires=REQUIRES,
    packages=[
        'spoon',
    ],
)
