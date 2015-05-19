#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flask-CDN-NG
---------

Serve the static files in your Flask app from a CDN.
"""
from setuptools import setup


setup(
    name='Flask-CDN-NG',
    version='1.3.0',
    url='https://github.com/s-m-i-t-a/flask-cdn-ng',
    license='MIT',
    author='Jindřich K. Smitka',
    author_email='smitka.j@gmail.com',
    description='Serve the static files in your Flask app from a CDN.',
    long_description=__doc__,
    py_modules=['flask_cdn'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'requests',
    ],
    test_suite='tests',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
