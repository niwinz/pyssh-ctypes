.. pyssh documentation master file, created by
   sphinx-quickstart on Tue Oct 30 20:27:51 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

================
py-libssh-ctypes
================

Is a python, object oriented wrapper for libssh build with ctypes.

Dependences:

* libssh >= 0.5

Features
--------

* SSH command execution with streaming api.
* SFTP subsystem with random access to remote files.
* Compatible with python3, python2 and pypy.


How to install
--------------

For normal use, you can use a standard python distutils ``setup.py`` file::

    python setup.py install

Or::

    pip install py-libssh-ctypes


Contents:
=========

.. toctree::
   :maxdepth: 2

   example
   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

