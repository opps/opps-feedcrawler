#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

from opps import feedcrawler


install_requires = ["opps"]

classifiers = ["Development Status :: 4 - Beta",
               "Intended Audience :: Developers",
               "License :: OSI Approved :: MIT License",
               "Operating System :: OS Independent",
               "Framework :: Django",
               'Programming Language :: Python',
               "Programming Language :: Python :: 2.7",
               "Operating System :: OS Independent",
               "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
               'Topic :: Software Development :: Libraries :: Python Modules']

try:
    long_description = open('README.md').read()
except:
    long_description = feedcrawler.__description__

setup(
    name='opps-feedcrawler',
    namespace_packages=['opps', 'opps.feedcrawler'],
    version=feedcrawler.__version__,
    description=feedcrawler.__description__,
    long_description=long_description,
    classifiers=classifiers,
    keywords='poll opps cms django apps magazines websites',
    author=feedcrawler.__author__,
    author_email=feedcrawler.__email__,
    url='http://oppsproject.org',
    download_url="https://github.com/opps/opps-feedcrawler/tarball/master",
    license=feedcrawler.__license__,
    packages=find_packages(exclude=('doc', 'docs',)),
    package_dir={'opps': 'opps'},
    install_requires=install_requires,
)
