#!/usr/bin/env/python
import os
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README")).read()

setup(
    name                    = "cloggy",
    version                 = "0.0",
    description             = "Exception tracker for python web-projects",
    long_description        = README,
    classifiers             = [
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Natural Language :: Russian",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: System :: Logging",        
    ],
    author                  = "vas3k",
    author_email            = "me@vas3k.ru",
    url                     = "http://vas3k.ru/dev/loggy/",
    keywords                = "web error exception logging log",
    packages                = find_packages(),
    include_package_data    = True,
    zip_safe                = False,
    install_requires        = [
        "django>=1.4",
        "sqlalchemy>=0.7.5",
    ]
)
