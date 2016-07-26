#! /usr/bin/env python

from __future__ import absolute_import

import spoon
import distutils.core

REQUIRES = []
DESCRIPTION = """Simple to use pre-forking server interface."""

CLASSIFIERS = [
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Intended Audience :: System Administrators",
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
]

distutils.core.setup(
    name='se-server',
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
