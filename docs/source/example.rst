==============
Usage examples
==============


Simple command execution
------------------------

.. code-block:: python

    >>> import pyssh
    >>> s = pyssh.connect()
    >>> r = s.execute("uname -a")
    >>> r.as_bytes()
    b'Linux vaio.niwi.be 3.5.3-1-ARCH #1 SMP PREEMPT Sun Aug 26 09:14:51 CEST 2012 x86_64 GNU/Linux\n'
    >>> r.return_code
    0


Random access on remote file with sftp
--------------------------------------

.. code-block:: python

    >>> import os
    >>> import pyssh
    >>> session = pyssh.connect("localhost")
    >>> sftp = pyssh.Sftp(session)
    >>> f = sftp.open("/tmp/some-file", (os.O_RDWR | os.O_CREAT))
    >>> f.tell()
    0
    >>> f.write(b'Hello World')
    >>> f.tell()
    11
    >>> f.seek(0)
    True
    >>> f.read(5)
    b'Hello'
    >>> f.read()
    b' World'
