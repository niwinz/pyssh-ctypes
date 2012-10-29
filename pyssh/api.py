# -*- coding: utf-8 -*-

import ctypes
import ctypes.util

__all__ = ['library']


def load_library():
    libpath = ctypes.util.find_library('ssh')
    libssh = ctypes.CDLL(libpath)
    return libssh

SSH_OK = 0
SSH_ERROR = -1
SSH_AGAIN = -2
SSH_EOF = -127

SSH_OPTIONS_HOST = 0
SSH_OPTIONS_PORT = 1
SSH_OPTIONS_PORT_STR = 2
SSH_OPTIONS_FD = 3
SSH_OPTIONS_USER = 4
SSH_OPTIONS_SSH_DIR = 5
SSH_OPTIONS_IDENTITY = 6
# TODO...

SSH_AUTH_SUCCESS = 0
SSH_AUTH_DENIED = 1
SSH_AUTH_PARTIAL = 2
SSH_AUTH_INFO = 3
SSH_AUTH_AGAIN = 4
SSH_AUTH_ERROR = -1


try:
    library = load_library()
    library.ssh_new.argtypes = []
    library.ssh_new.restype = ctypes.c_void_p

    library.ssh_free.argtypes = [ctypes.c_void_p]

    library.ssh_connect.argtypes = [ctypes.c_void_p]
    library.ssh_connect.restype = ctypes.c_int

    library.ssh_disconnect.argtypes = [ctypes.c_void_p]
    library.ssh_options_set.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]

    library.ssh_userauth_password.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    library.ssh_userauth_password.restype = ctypes.c_int

    library.ssh_userauth_autopubkey.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    library.ssh_userauth_autopubkey.restype = ctypes.c_int

    library.ssh_channel_new.argtypes = [ctypes.c_void_p]
    library.ssh_channel_new.restype = ctypes.c_void_p

    library.ssh_channel_open_session.argtypes = [ctypes.c_void_p]
    library.ssh_channel_open_session.restype = ctypes.c_int

    library.ssh_channel_request_exec.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    library.ssh_channel_request_exec.restype = ctypes.c_int

    library.ssh_channel_read.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_int]
    library.ssh_channel_read.restype = ctypes.c_int

    library.ssh_channel_send_eof.argtypes = [ctypes.c_void_p]
    library.ssh_channel_send_eof.restype = ctypes.c_int

    library.ssh_channel_free.argtypes = [ctypes.c_void_p]

    library.ssh_channel_get_exit_status.argtypes = [ctypes.c_void_p]
    library.ssh_channel_get_exit_status.restype = ctypes.c_int

    library.ssh_get_error.argtypes = [ctypes.c_void_p]
    library.ssh_get_error.restype = ctypes.c_char_p

    # SFTP
    library.sftp_new.argtypes = [ctypes.c_void_p]
    library.sftp_new.restype = ctypes.c_void_p

    library.sftp_free.argtypes = [ctypes.c_void_p]

    library.sftp_open.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
    library.sftp_open.restype = ctypes.c_void_p

    library.sftp_close.argtypes = [ctypes.c_void_p]

    library.sftp_write.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint]
    library.sftp_write.restype = ctypes.c_int

    library.sftp_seek64.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong]
    library.sftp_seek64.restype = ctypes.c_int

    library.sftp_tell64.argtypes = [ctypes.c_void_p]
    library.sftp_tell64.restype = ctypes.c_ulonglong

    library.sftp_read.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
    library.sftp_read.restype = ctypes.c_int

except AttributeError:
    raise ImportError('ssh shared library not found or incompatible')
except (OSError, IOError):
    raise ImportError('ssh shared library not found.\n'
                      'you probably had not installed libssh library.\n')
