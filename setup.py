#!/usr/bin/env python
from distutils.core import setup

version='2.0.0'

setup(
    name='vkontakte',
    version=version,
    author='Mikhail Korobov, Serhii Maltsev',
    author_email='kmike84@gmail.com, alternativshik@gmail.com',

    packages=['vkontakte'],

    url='http://bitbucket.org/kmike/vkontakte/',
    license = 'MIT license',
    description = "vk.com (aka vkontakte.ru) API wrapper",

    long_description = open('README.rst').read() + open('CHANGES.rst').read(),

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
