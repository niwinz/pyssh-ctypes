# -*- coding: utf-8 -*-

class PySshException(Exception):
    pass


class AuthenticationError(PySshException):
    pass


class ConnectionError(PySshException):
    pass
