# -*- coding: utf-8 -*-

class SshError(Exception):
    pass


class AuthenticationError(SshError):
    pass


class ConnectionError(SshError):
    pass


class ResourceManagementError(SshError):
    pass
