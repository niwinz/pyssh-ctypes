# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .session import Session
from .sftp import Sftp


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
    try:
        session.connect()
    except Exception as e:
        # Free resources on any exception is raised
        session.close()
        raise

    return session


__all__ = ['connect', 'Session', 'Sftp']
