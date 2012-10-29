# -*- coding: utf-8 -*-

from . import api
import ctypes


class Result(object):
    _return_code = None
    _consumed = False

    def __init__(self, session, command):
        self.session = session
        self.command = command

    def __iter__(self):
        if self._consumed:
            raise RuntimeError("Result are consumed")

        self._consumed = True

        channel = api.library.ssh_channel_new(self.session);
        ret = api.library.ssh_channel_open_session(channel)
        if ret != api.SSH_OK:
            raise RuntimeError("Error code: {0}".format(ret))

        ret = api.library.ssh_channel_request_exec(channel, self.command)
        if ret != api.SSH_OK:
            msg = api.library.ssh_get_error(self.session)
            raise RuntimeError("Error {0}: {1}".format(ret, msg.decode('utf-8')))

        while True:
            data = ctypes.create_string_buffer(10)
            readed_bytes = api.library.ssh_channel_read(channel, ctypes.byref(data), len(data), 0)
            if readed_bytes > 0:
                yield data.value
            else:
                api.library.ssh_channel_send_eof(channel);
                self._return_code = api.library.ssh_channel_get_exit_status(channel)
                break

        api.library.ssh_channel_free(channel)

    def as_bytes(self):
        return b"".join([x for x in self])

    def as_str(self):
        return self.as_bytes().decode("utf-8")

    @property
    def return_code(self):
        return self._return_code


class Session(object):
    session = None
    username = None
    password = None

    _closed = True

    def __init__(self, hostname, port, username=None, password=None, passphrase=None):
        self.session = api.library.ssh_new()

        if isinstance(hostname, str):
            self.hostname = bytes(hostname, "utf-8")
        else:
            self.hostname = hostname

        if isinstance(port, int):
            self.port = bytes(str(int), "utf-8")
        elif isinstance(port, str):
            self.port = bytes(port, "utf-8")
        else:
            self.port = port

        if isinstance(username, str):
            self.username = bytes(username, "utf-8")
        else:
            self.username = username

        if isinstance(password, str):
            self.password = bytes(password, "utf-8")
        else:
            self.password = password

        if self.username:
            api.library.ssh_options_set(this.session, api.SSH_OPTIONS_USER, self.username)

        if isinstance(passphrase, str):
            self.passphrase = bytes(passphrase, "utf-8")
        else:
            self.passphrase = passphrase

        api.library.ssh_options_set(self.session, api.SSH_OPTIONS_PORT_STR, self.port)
        api.library.ssh_options_set(self.session, api.SSH_OPTIONS_HOST, self.hostname)

    def connect(self):
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

    def execute(self, command):
        if isinstance(command, str):
            command = bytes(command, "utf-8")

        return Result(self.session, command)

    def close(self):
        if self._closed:
            raise RuntimeError("Already closed")

        self._closed = True
        api.library.ssh_disconnect(self.session)

    def __del__(self):
        if self.session is not None:
            api.library.ssh_free(self.session)


def connect(hostname="localhost", port="22", username=None, password=None):
    session = Session(hostname=hostname, port=port, username=username, password=password)
    session.connect()
    return session
