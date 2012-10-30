# -*- coding: utf-8 -*-

from distutils.core import Extension, setup


setup(
    name='pyssh-ctypes',
    version='0.1.0',
    description='Python bingings for libssh build on top of boost.python',
    author='Andrey Antukh',
    author_email='niwi@niwi.be',

    url='https://github.com/niwibe/py-libssh',
    packages = ['pyssh'],

    classifiers = [
        "Development Status :: 4 - Beta",
        "Topic :: System :: Systems Administration",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: BSD :: NetBSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
    ]
)
