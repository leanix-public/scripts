#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup routine."""

from setuptools import find_packages, setup

setup(
    name='leanix-python-client-template',
    version='0.0.1',
    author='LeanIX GmbH',
    author_email='support@leanix.net',
    description='A template for creating new projects using the leanix-python-client',
    keywords='development',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests',
        'six',
        'leanix-python-client'
    ],
    license='Apache 2.0'
)
