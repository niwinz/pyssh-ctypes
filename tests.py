# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import io
import os
import sys
import shutil
import unittest
import importlib
import hashlib

class PythonLibsshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Add build directory to python path
        cls.pyssh = importlib.import_module("pyssh")
        cls.pyssh_result = importlib.import_module("pyssh.result")
        cls.pyssh_exp = importlib.import_module("pyssh.exceptions")

        with io.open("/tmp/py-libssh.temp.file", "wb") as f:
            f.write(b"aaaaaaaaa\n")
            f.write(b"bbbbbbbbb\n")
            f.write(b"ccccccccc\n")

    @classmethod
    def tearDownClass(cls):
        os.remove("/tmp/py-libssh.temp.file")

    def test_auth_with_password(self):
        # NOTE: this test asumes that your sistem has
        # test user with test password.
        with self.pyssh.new_session(username="test", password="test") as s:
            r = s.execute("id", lazy=False)
            result = r.as_bytes()
            self.assertEqual(result, b"uid=1001(test) gid=1001(test) groups=1001(test)\n")

    def test_auth_with_wrong_password(self):
        # NOTE: this test asumes that your sistem has
        # test user with test password.

        with self.assertRaises(self.pyssh_exp.AuthenticationError):
            s = self.pyssh.new_session(username="test", password="test2", connect_on_init=True)

    def test_new_session_and_execute_command_not_lazy(self):
        with self.pyssh.new_session() as s:
            r = s.execute("uname", lazy=False)
            result = r.as_bytes()
            return_code = r.return_code

            self.assertEqual(return_code, 0)
            self.assertEqual(result, b"Linux\n")
            self.assertIsInstance(r, self.pyssh_result.Result)

    def test_new_session_and_execute_command_01(self):
        with self.pyssh.new_session() as s:
            r = s.execute("uname", lazy=True)
            result = r.as_bytes()
            return_code = r.return_code

            self.assertEqual(return_code, 0)
            self.assertEqual(result, b"Linux\n")
            self.assertIsInstance(r, self.pyssh_result.LazyResult)

    def test_new_session_and_execute_command_02(self):
        with self.pyssh.new_session() as s:
            r = s.execute("uname", lazy=True)
            result = r.as_bytes()

            with self.assertRaises(RuntimeError):
                result = r.as_bytes()

    #def test_new_session_and_execute_command_02(self):
    #    s = self.pyssh.new_session()
    #    r = s.execute("echo $FOO", env={"FOO": "Hello"})
    #    result = r.as_bytes()
    #    self.assertEqual(result, b"Hello")

    def test_new_session_and_put(self):
        sha1_1 = hashlib.sha1()
        with io.open("/tmp/py-libssh.temp.file.2", "wb") as f:
            data = b"FOOOO" * 20
            sha1_1.update(data)
            f.write(data)

        with self.pyssh.new_session() as s, s.create_sftp() as sftp:
            sftp.put("/tmp/py-libssh.temp.file.2", "/tmp/py-libssh.temp.file.3")

        self.assertTrue(os.path.exists("/tmp/py-libssh.temp.file.3"))

        sha1_2 = hashlib.sha1()
        with io.open("/tmp/py-libssh.temp.file.3", "rb") as f:
            sha1_2.update(f.read())

        self.assertEqual(sha1_2.hexdigest(), sha1_1.hexdigest())

        os.remove("/tmp/py-libssh.temp.file.2")
        os.remove("/tmp/py-libssh.temp.file.3")

    def test_new_session_and_get(self):
        sha1_1 = hashlib.sha1()
        with io.open("/tmp/py-libssh.temp.file.2", "wb") as f:
            data = b"FOOOO" * 20
            sha1_1.update(data)
            f.write(data)

        with self.pyssh.new_session() as s, s.create_sftp() as sftp:
            sftp.get("/tmp/py-libssh.temp.file.2", "/tmp/py-libssh.temp.file.3")

        self.assertTrue(os.path.exists("/tmp/py-libssh.temp.file.3"))

        sha1_2 = hashlib.sha1()
        with io.open("/tmp/py-libssh.temp.file.3", "rb") as f:
            sha1_2.update(f.read())

        self.assertEqual(sha1_2.hexdigest(), sha1_1.hexdigest())

        os.remove("/tmp/py-libssh.temp.file.2")
        os.remove("/tmp/py-libssh.temp.file.3")

    def test_new_session_and_get_huge_file(self):
        sha1_1 = hashlib.sha1()

        with io.open("/tmp/py-libssh.temp.file.2", "wb") as f:
            data = b"K" * 10485760
            sha1_1.update(data)
            f.write(data)

        with self.pyssh.new_session() as s, s.create_sftp() as sftp:
            sftp.get("/tmp/py-libssh.temp.file.2", "/tmp/py-libssh.temp.file.3")

        self.assertTrue(os.path.exists("/tmp/py-libssh.temp.file.3"))

        sha1_2 = hashlib.sha1()
        with io.open("/tmp/py-libssh.temp.file.3", "rb") as f:
            sha1_2.update(f.read())

        self.assertEqual(sha1_2.hexdigest(), sha1_1.hexdigest())

        os.remove("/tmp/py-libssh.temp.file.2")
        os.remove("/tmp/py-libssh.temp.file.3")


    def test_read_remote_file(self):
        with self.pyssh.new_session() as s, s.create_sftp() as sftp:
            f = sftp.open("/tmp/py-libssh.temp.file", os.O_RDONLY)
            self.assertEqual(b"aaaaaaaaa\n", f.read(10))

    #def test_shell_01(self):
    #    import pdb; pdb.set_trace()
    #    session = self.pyssh.new_session()
    #    shell = session.shell()
    #    #x = shell.read(1024)
    #    #shell.write("echo $USER;\n")
