================
py-libssh-ctypes
================

Python wrapper for libssh build on top of ctypes.
With full streaming api.

Tested with:

* Python 3.3
* Python 2.7
* Pypy 1.9

Dependences:

* libssh >= 0.5


How to install
--------------

For normal use, you can use a standard python distutils ``setup.py`` file::

    python setup.py install


Api reference:
--------------

`pyssh.connect(hostname="localhost", port=22, username=None, password=None, passphrase=None)`
    Creates ssh session and connects to corresponding host and port. By default intent autenticate with local pubkey.
    If passwrod and username are provided, normal user and password authentication is executed instead of a pubkey.

    This returns ``pyssh.base.Session`` instance.


``pyssh.base.Session``
^^^^^^^^^^^^^^^^^

Represents a ssh connection.

``pyssh.base.Session.execute(command)``
    Executes some command on a remote machine. Returns ``pyssh.base.Result`` instance.


``pyssh.base.Result``
^^^^^^^^^^^^^^^^

Represents a result of execution of command on ssh session. Result by default, does not download all the content, but you have to iterate over all output for command execution. (The content is obtained from the server in chucks of 1024 bytes)

``pyssh.base.Result.__iter__()``
    Returns itself as iterator.

``pyssh.base.Result.return_code``
    Command execution return code. Only avaliable over all iteration.

``pyssh.base.Result.as_str()``
    Return unicode string of all command execution output.

``pyssh.base.Result.as_bytes()``
    Same as that, ``as_str()`` but returns a bytes.


Examples
--------

Command execution example.

.. code-block:: python 

    >>> import pyssh
    >>> s = pyssh.connect()
    >>> r = s.execute("uname -a")
    >>> r.as_bytes()
    b'Linux vaio.niwi.be 3.5.3-1-ARCH #1 SMP PREEMPT Sun Aug 26 09:14:51 CEST 2012 x86_64 GNU/Linux\n'
    >>> r.return_code
    0
