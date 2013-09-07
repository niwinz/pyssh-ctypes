# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ctypes
import stat
import os
import io

from . import compat
from . import api


class Sftp(object):
    """
    Sftp wrapper.

    Exposes api for interacting with sftp subsystem: put or get files,
    open files with random read-write access, etc.

    :ivar ponter sftp: c sftp session pointer
    :ivar pointer session: c ssh session pointer

    :param pyssh.Session session: initialized and connected
        :py:class:`pyssh.Session` instance.
    """

    sftp = None
    session = None

    def __init__(self, session):
        self.session_wrapper = session
        self.session = session.session

        self.sftp = api.library.sftp_new(self.session)


    def get(self, remote_path, local_path):
        """
        Get a remote file to local.

        :param str remote_path: remote file path
        :param str local_path:  local file path
        """
        if isinstance(remote_path, compat.text_type):
            remote_path = compat.to_bytes(remote_path)

        access_type = os.O_RDONLY
        remote_file = api.library.sftp_open(self.sftp, remote_path, access_type, stat.S_IRWXU)

        with io.open(local_path, "wb") as f:
            while True:
                buffer = ctypes.create_string_buffer(1024)
                readed = api.library.sftp_read(remote_file, ctypes.byref(buffer),  1024);

                if readed == 0:
                    break

                f.write(buffer.value)

    def put(self, path, remote_path):
        """
        Puts the local file to remote host.

        :param str path: local file path
        :param str remote_path: remote file path
        """

        if not os.path.exists(path):
            raise RuntimeError("Path {0} does not exists".format(path))

        if isinstance(remote_path, compat.text_type):
            remote_path = compat.to_bytes(remote_path, "utf-8")

        access_type = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        remote_file = api.library.sftp_open(self.sftp, remote_path, access_type, stat.S_IRWXU);

        with io.open(path, "rb") as f:
            while True:
                chuck = f.read(1024)
                if not chuck:
                    break

                written = api.library.sftp_write(remote_file, chuck, len(chuck))
                if written != len(chuck):
                    raise RuntimeError("Can't write file")

        api.library.sftp_close(remote_file)

    def open(self, path, mode):
        """
        Open a remote file.

        :param str path: remote file path
        :param int mode: open file model (see http://docs.python.org/3.3/library/os.html#open-flag-constants)

        :returns: SFTP File wrapper
        :rtype: pyssh.SftpFile
        """
        if isinstance(path, compat.text_type):
            path = compat.to_bytes(path, "utf-8")

        return SftpFile(path, mode, self)

    def __del__(self):
        if self.sftp is not None:
            api.library.sftp_free(self.sftp)


class SftpFile(object):
    """
    SFTP File wrapper
    """

    _closed = False

    def __init__(self, path, mode, sftp_wrapper):
        self.sftp_wrapper = sftp_wrapper
        self.sftp = sftp_wrapper.sftp

        self.file = api.library.sftp_open(self.sftp, path, mode, stat.S_IRWXU)

        if self.file is None:
            self._closed = True
            raise RuntimeError("Can't open file {0}".format(path.decode("utf-8")))

    def write(self, data):
        """
        Write bytes to remote file.

        :param bytes data: bytes chunk of data
        :returns: number of bytes are written
        :rtype: int
        """
        written = api.library.sftp_write(self.file, data, len(data))
        if written != len(data):
            raise RuntimeError("Can't write file")

        return written

    def read(self, num=None):
        """
        Read from remote file.

        :param int num: number of bytes to read, if num is None reads all.
        :returns: readed bytes chunk
        :rtype: bytes
        """
        if num is None:
            buffer_len = 1024
        else:
            buffer_len = num

        buffer = ctypes.create_string_buffer(buffer_len)
        readed = api.library.sftp_read(self.file, ctypes.byref(buffer),  buffer_len);

        if readed == 0:
            return b""

        if num is not None and num > 0:
            if buffer_len != readed:
                raise RuntimeError("Error on read")
            return buffer.value

        readed_data = [buffer.value]
        while True:
            buffer = ctypes.create_string_buffer(buffer_len)
            readed = api.library.sftp_read(self.file, ctypes.byref(buffer),  buffer_len);
            if readed == 0:
                break

            readed_data.append(buffer.value)
        return b"".join(readed_data)

    def seek(self, offset):
        """
        Change position on a remote file.

        :param int offset: file position
        :returns: boolean value if seek is success or not
        :rtype: bool
        """
        ret = api.library.sftp_seek64(self.file, offset);
        if ret != api.SSH_OK:
            return False

        return True

    def tell(self):
        """
        Query the current position on a file.

        :returns: a current position.
        :rtype: int
        """
        return api.library.sftp_tell64(self.file)

    def close(self):
        """
        Close a opened file.
        """
        if self._closed:
            raise RuntimeError("Already closed")

        self._closed = True
        api.library.sftp_close(self.file)
