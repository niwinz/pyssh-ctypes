# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='pyssh-ctypes',
    version='0.3',
    description='Python bindings for libssh on top of ctypes',
    author='Andrey Antukh',
    author_email='niwi@niwi.be',

    url='https://github.com/niwibe/py-libssh',
    packages = ['pyssh'],
    install_requires = ["six >=1.4.1"],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Topic :: System :: Systems Administration",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: BSD :: NetBSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
    ]
)
