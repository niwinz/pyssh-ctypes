# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import warnings

from . import api
from . import compat
from . import result
from . import exceptions as exp
from . import shell


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

        if isinstance(hostname, compat.text_type):
            self.hostname = compat.to_bytes(hostname)
        else:
            self.hostname = hostname

        if isinstance(port, int):
            self.port = compat.to_bytes(str(port))
        elif isinstance(port, compat.text_type):
            self.port = compat.to_bytes(port)
        else:
            self.port = port

        if isinstance(username, compat.text_type):
            self.username = compat.to_bytes(username)
        else:
            self.username = username

        if isinstance(password, compat.text_type):
            self.password = compat.to_bytes(password)
        else:
            self.password = password

        if self.username:
            api.library.ssh_options_set(self.session, api.SSH_OPTIONS_USER, self.username)

        if isinstance(passphrase, compat.text_type):
            self.passphrase = compat.to_bytes(passphrase, "utf-8")
        else:
            self.passphrase = passphrase

        api.library.ssh_options_set(self.session, api.SSH_OPTIONS_PORT_STR, self.port)
        api.library.ssh_options_set(self.session, api.SSH_OPTIONS_HOST, self.hostname)

    def connect(self):
        """
        Initialize the connection with remote host.

        This method souldn't be used normally, because it is called automatically
        by the :py:func:`pyssh.connect` function.
        """

        if not self._closed:
            raise exp.ConnectionError("Already connected")

        self._closed = False

        ret = api.library.ssh_connect(self.session)
        if ret != api.SSH_OK:
            msg = api.library.ssh_get_error(self.session)
            raise exp.ConnectionError("Error {0}: {1}".format(ret, msg.decode('utf-8')))

        self._closed = False

        if self.password:
            ret = api.library.ssh_userauth_password(self.session, None, self.password)
            if ret != api.SSH_AUTH_SUCCESS:
                raise exp.AuthenticationError("Error when trying authenticate with password. "
                                              "(Error code: {0})".format(ret))
        else:
            ret = api.library.ssh_userauth_autopubkey(self.session, self.passphrase)
            if ret != api.SSH_AUTH_SUCCESS:
                raise exp.AuthenticationError("Error when trying authenticate with pubkey. "
                                              "(Error code: {0})".format(ret))

    def close(self):
        """
        Close initialized ssh connection.
        """
        if self._closed:
            raise RuntimeError("Already closed")

        self._closed = True
        api.library.ssh_disconnect(self.session)

    def shell(self, pty_size=(80, 24), env={}):
        """
        :param tuple pty_size: in case of shell is true this indicates
            the size of a virtual terminal
        :param dict env: addiotional environ variables
        """
        warnings.warn("Shell feature is very experimental and uncomplete.", Warning)
        return shell.Shell(self.session, pty_size, env)

    def execute(self, command, lazy=False):
        """
        Execute command on remote host.

        :param str command: command string
        :param bool lazy: set true for return a lazy result
                          instead a evalueted. Useful for execute
                          commands with large output (default: False)

        :returns: Result instance
        :rtype: :py:class:`pyssh.result.Result`
        """

        if isinstance(command, compat.text_type):
            command = compat.to_bytes(command)

        if lazy:
            _result = result.LazyResult(self.session, command)
        else:
            _result = result.Result(self.session, command)
        return _result

    def __del__(self):
        if self.session is not None:
            api.library.ssh_free(self.session)
