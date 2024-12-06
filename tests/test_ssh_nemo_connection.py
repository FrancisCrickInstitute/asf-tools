"""
Tests for the Nemo module.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,invalid-name

import unittest
from unittest.mock import MagicMock, patch

from asf_tools.ssh.nemo import Nemo


class TestNemoConnection(unittest.TestCase):

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_init_with_key_file(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq", key_file="/path/to/key")
        MockConnection.assert_called_once_with(host="login.nemo.thecrick.org", user="svc-asf-seq", connect_kwargs={"key_filename": "/path/to/key"})
        self.assertIsNotNone(nemo.connection)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_init_with_password(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq", password="password")
        MockConnection.assert_called_once_with(host="login.nemo.thecrick.org", user="svc-asf-seq", connect_kwargs={"password": "password"})
        self.assertIsNotNone(nemo.connection)

    def test_nemo_init_without_key_or_password(self):
        with self.assertRaises(ValueError):
            Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq")

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_disconnect(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq", password="password")
        nemo.disconnect()
        MockConnection().close.assert_called_once()
        self.assertIsNone(nemo.connection)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_run_command(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = "command output"
        mock_result.stderr.strip.return_value = "error output"
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        stdout, stderr = nemo.run_command("ls -las")

        MockConnection().run.assert_called_once_with("ls -las", hide=True)
        self.assertEqual(stdout, "command output")
        self.assertEqual(stderr, "error output")

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_list_directory_objects(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = (
            "total 8\n"
            "drwxr-xr-x 2 user group 4096 2023-10-01 12:34 .\n"
            "drwxr-xr-x 3 user group 4096 2023-10-01 12:34 ..\n"
            "-rw-r--r-- 1 user group 1234 2023-10-01 12:34 test_file.txt\n"
            "lrwxrwxrwx 1 user group 1234 2023-10-01 12:34 link -> target"
        )
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        files = nemo.list_directory_objects("~")

        MockConnection().run.assert_called_once_with("cd ~ && ls -la --time-style=long-iso", hide=True)
        self.assertEqual(len(files), 4)
        self.assertEqual(files[0].name, ".")
        self.assertEqual(files[1].name, "..")
        self.assertEqual(files[2].name, "test_file.txt")
        self.assertEqual(files[3].name, "link")
        self.assertEqual(files[3].link_target, "target")

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_list_directory(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = (
            "total 8\n"
            "drwxr-xr-x 2 user group 4096 2023-10-01 12:34 .\n"
            "drwxr-xr-x 3 user group 4096 2023-10-01 12:34 ..\n"
            "-rw-r--r-- 1 user group 1234 2023-10-01 12:34 test_file.txt\n"
            "lrwxrwxrwx 1 user group 1234 2023-10-01 12:34 link -> target"
        )
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        files = nemo.list_directory("~")

        MockConnection().run.assert_called_once_with("cd ~ && ls -la --time-style=long-iso", hide=True)
        self.assertEqual(len(files), 4)
        self.assertEqual(files[0], ".")
        self.assertEqual(files[1], "..")
        self.assertEqual(files[2], "test_file.txt")
        self.assertEqual(files[3], "link")

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_exists(self, MockConnection):
        mock_result = MagicMock()
        mock_result.ok = True
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        result = nemo.exists("~")

        MockConnection().run.assert_called_once_with("test -e ~", hide=True)
        self.assertTrue(result)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_nemo_exists_with_pattern(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = "test_file.txt"
        MockConnection().run.return_value = mock_result

        nemo = Nemo(host="login.nemo.thecrick.org", user="user", password="password")
        result = nemo.exists_with_pattern("/home/user", "test_file.txt")

        MockConnection().run.assert_called_once_with("find /home/user -maxdepth 1 -name test_file.txt", hide=True)
        self.assertTrue(result)

    def test_nemo_dev(self):
        nemo = Nemo(host="login007.nemo.thecrick.org", user="cheshic", key_file="/Users/cheshic/.ssh/nemo_rsa")
        test = nemo.exists_with_pattern(".", ".v*")

        print(test)

        raise NotImplementedError("Test not implemented")
