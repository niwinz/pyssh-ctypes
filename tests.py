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
        s = self.pyssh.connect(username="test", password="test")
        r = s.execute("id", lazy=False)

        result = r.as_bytes()
        self.assertEqual(result, b"uid=1001(test) gid=1001(test) groups=1001(test)\n")

    def test_connect_and_execute_command_not_lazy(self):
        s = self.pyssh.connect()
        r = s.execute("uname", lazy=False)
        result = r.as_bytes()
        return_code = r.return_code

        self.assertEqual(return_code, 0)
        self.assertEqual(result, b"Linux\n")
        self.assertIsInstance(r, self.pyssh_result.Result)

    def test_connect_and_execute_command_01(self):
        s = self.pyssh.connect()
        r = s.execute("uname", lazy=True)
        result = r.as_bytes()
        return_code = r.return_code

        self.assertEqual(return_code, 0)
        self.assertEqual(result, b"Linux\n")
        self.assertIsInstance(r, self.pyssh_result.LazyResult)

    def test_connect_and_execute_command_02(self):
        s = self.pyssh.connect()
        r = s.execute("uname", lazy=True)
        result = r.as_bytes()

        with self.assertRaises(RuntimeError):
            result = r.as_bytes()

    #def test_connect_and_execute_command_02(self):
    #    s = self.pyssh.connect()
    #    r = s.execute("echo $FOO", env={"FOO": "Hello"})
    #    result = r.as_bytes()
    #    self.assertEqual(result, b"Hello")

    def test_connect_and_put(self):
        sha1_1 = hashlib.sha1()
        with io.open("/tmp/py-libssh.temp.file.2", "wb") as f:
            data = b"FOOOO" * 20
            sha1_1.update(data)
            f.write(data)

        session = self.pyssh.connect()
        sftp = self.pyssh.Sftp(session)
        sftp.put("/tmp/py-libssh.temp.file.2", "/tmp/py-libssh.temp.file.3")

        self.assertTrue(os.path.exists("/tmp/py-libssh.temp.file.3"))

        sha1_2 = hashlib.sha1()
        with io.open("/tmp/py-libssh.temp.file.3", "rb") as f:
            sha1_2.update(f.read())

        self.assertEqual(sha1_2.hexdigest(), sha1_1.hexdigest())

        os.remove("/tmp/py-libssh.temp.file.2")
        os.remove("/tmp/py-libssh.temp.file.3")

    def test_connect_and_get(self):
        sha1_1 = hashlib.sha1()
        with io.open("/tmp/py-libssh.temp.file.2", "wb") as f:
            data = b"FOOOO" * 20
            sha1_1.update(data)
            f.write(data)

        session = self.pyssh.connect()
        sftp = self.pyssh.Sftp(session)
        sftp.get("/tmp/py-libssh.temp.file.2", "/tmp/py-libssh.temp.file.3")

        self.assertTrue(os.path.exists("/tmp/py-libssh.temp.file.3"))

        sha1_2 = hashlib.sha1()
        with io.open("/tmp/py-libssh.temp.file.3", "rb") as f:
            sha1_2.update(f.read())

        self.assertEqual(sha1_2.hexdigest(), sha1_1.hexdigest())

        os.remove("/tmp/py-libssh.temp.file.2")
        os.remove("/tmp/py-libssh.temp.file.3")

    def test_connect_and_get_huge_file(self):
        sha1_1 = hashlib.sha1()

        with io.open("/tmp/py-libssh.temp.file.2", "wb") as f:
            data = b"K" * 10485760
            sha1_1.update(data)
            f.write(data)

        session = self.pyssh.connect()
        sftp = self.pyssh.Sftp(session)
        sftp.get("/tmp/py-libssh.temp.file.2", "/tmp/py-libssh.temp.file.3")

        self.assertTrue(os.path.exists("/tmp/py-libssh.temp.file.3"))

        sha1_2 = hashlib.sha1()
        with io.open("/tmp/py-libssh.temp.file.3", "rb") as f:
            sha1_2.update(f.read())

        self.assertEqual(sha1_2.hexdigest(), sha1_1.hexdigest())

        os.remove("/tmp/py-libssh.temp.file.2")
        os.remove("/tmp/py-libssh.temp.file.3")


    def test_read_remote_file(self):
        session = self.pyssh.connect()
        sftp = self.pyssh.Sftp(session)
        f = sftp.open("/tmp/py-libssh.temp.file", os.O_RDONLY)
        self.assertEqual(b"aaaaaaaaa\n", f.read(10))

    #def test_shell_01(self):
    #    import pdb; pdb.set_trace()
    #    session = self.pyssh.connect()
    #    shell = session.shell()
    #    #x = shell.read(1024)
    #    #shell.write("echo $USER;\n")
