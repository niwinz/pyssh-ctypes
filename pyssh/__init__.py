# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from . import api

import ctypes
import stat
import sys
import os
import io

# Python 2.7 compatibility layer

if sys.version_info.major < 3:
    def bytes(data, encoding="utf-8"):
        return data.encode(encoding)

    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes


class Result(object):
    """
    Lazy command execution result wrapper.

    This wrapper implements a iterator interface.
    """

    _return_code = None
    _consumed = False

    def __init__(self, session, command):
        self.session = session
        self.command = command

    def __next__(self):
        if self._finished:
            raise StopIteration()

        data = ctypes.create_string_buffer(10)
        readed_bytes = api.library.ssh_channel_read(self.channel, ctypes.byref(data), len(data), 0)
        if readed_bytes > 0:
            return data.value

        api.library.ssh_channel_send_eof(self.channel);
        self._return_code = api.library.ssh_channel_get_exit_status(self.channel)
        api.library.ssh_channel_free(self.channel)
        self._finished = True
        raise StopIteration

    if sys.version_info.major == 2:
        next = __next__

    def __iter__(self):
        if self._consumed:
            raise RuntimeError("Result are consumed")

        self._consumed = True
        self._finished = False

        self.channel = api.library.ssh_channel_new(self.session);
        ret = api.library.ssh_channel_open_session(self.channel)
        if ret != api.SSH_OK:
            raise RuntimeError("Error code: {0}".format(ret))

        ret = api.library.ssh_channel_request_exec(self.channel, self.command)
        if ret != api.SSH_OK:
            msg = api.library.ssh_get_error(self.session)
            raise RuntimeError("Error {0}: {1}".format(ret, msg.decode('utf-8')))

        return self

    def as_bytes(self):
        """
        Launch the command and return a result as bytes.

        :returns: bytes chunk of command execution result
        :rtype: bytes
        """

        return b"".join([x for x in self])

    def as_str(self):
        """
        Launch the command and return a result as unicode string

        :returns: unicode chunk of command execution result
        :rtype: str/unicode
        """
        return self.as_bytes().decode("utf-8")

    def wait(self):
        """
        Waits a complete command execution and returns the return code

        :returns: execution result return code
        :rtype: int
        """
        list(self)
        return self.return_code

    @property
    def return_code(self):
        return self._return_code


class Session(object):
    """
    SSH Session wrapper.

    Actually accepts two methods for authentication: the simple a simple password or
    a pubkey. If password is not provided, attempts using pubkey, with or without pasphrase.

    :ivar pointer session: c ssh session pointer
    :ivar bytes username: current username

    :param str hostname: remote ip or host
    :param int port: remote port
    :param str username: remote user name with which you want to authenticate
    :param str password: remote user password.
    :param str passphrase: passphrase in case you would authenticate with pubkey
    """

    session = None
    username = None
    password = None

    _closed = True

    def __init__(self, hostname, port=22, username=None, password=None, passphrase=None):
        self.session = api.library.ssh_new()

        if isinstance(hostname, text_type):
            self.hostname = bytes(hostname, "utf-8")
        else:
            self.hostname = hostname

        if isinstance(port, int):
            self.port = bytes(str(int), "utf-8")
        elif isinstance(port, text_type):
            self.port = bytes(port, "utf-8")
        else:
            self.port = port

        if isinstance(username, text_type):
            self.username = bytes(username, "utf-8")
        else:
            self.username = username

        if isinstance(password, text_type):
            self.password = bytes(password, "utf-8")
        else:
            self.password = password

        if self.username:
            api.library.ssh_options_set(this.session, api.SSH_OPTIONS_USER, self.username)

        if isinstance(passphrase, text_type):
            self.passphrase = bytes(passphrase, "utf-8")
        else:
            self.passphrase = passphrase

        api.library.ssh_options_set(self.session, api.SSH_OPTIONS_PORT_STR, self.port)
        api.library.ssh_options_set(self.session, api.SSH_OPTIONS_HOST, self.hostname)

    def connect(self):
        """
        Initialize the connection with remote host.
        """

        if not self._closed:
            raise RuntimeError("Already connected")

        self._closed = False

        ret = api.library.ssh_connect(self.session)
        if ret != api.SSH_OK:
            msg = api.library.ssh_get_error(self.session)
            raise RuntimeError("Error {0}: {1}".format(ret, msg.decode('utf-8')))

        self._closed = False

        if self.password:
            ret = api.library.ssh_userauth_password(self.session, None, self.password)
            if ret != api.SSH_AUTH_SUCCESS:
                raise RuntimeError("Error code: {0}".format(ret))
        else:
            ret = api.library.ssh_userauth_autopubkey(self.session, self.passphrase)
            if ret != api.SSH_AUTH_SUCCESS:
                raise RuntimeError("Error code: {0}".format(ret))

    def close(self):
        """
        Close initialized ssh connection.
        """
        if self._closed:
            raise RuntimeError("Already closed")

        self._closed = True
        api.library.ssh_disconnect(self.session)

    def execute(self, command):
        """
        Execute command on remote host.

        :param str command: command string
        :returns: Lazy result instance
        :rtype: :py:class:`pyssh.Result`
        """
        if isinstance(command, text_type):
            command = bytes(command, "utf-8")

        return Result(self.session, command)

    def __del__(self):
        if self.session is not None:
            api.library.ssh_free(self.session)


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

    def put(self, path, remote_path):
        """
        Puts the local file to remote host.

        :param str path: local file path
        :param str remote_path: remote file path
        """

        if not os.path.exists(path):
            raise RuntimeError("Path {0} does not exists".format(path))

        if isinstance(remote_path, text_type):
            remote_path = bytes(remote_path, "utf-8")

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
        if isinstance(path, text_type):
            path = bytes(path, "utf-8")

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


def connect(hostname="localhost", port="22", username=None, password=None, passphrase=None):
    """
    Shortcut method for create session and connect to remote host.

    :param str hostname: remote ip or host
    :param int port: remote port
    :param str username: remote user name with which you want to authenticate
    :param str password: remote user password.
    :param str passphrase: passphrase in case you would authenticate with pubkey
    """
    session = Session(hostname=hostname, port=port, username=username,
                                password=password, passphrase=passphrase)
    session.connect()
    return session
