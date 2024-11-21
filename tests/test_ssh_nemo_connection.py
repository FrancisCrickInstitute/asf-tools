"""
Tests for the Nemo module.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,invalid-name

import unittest
from unittest.mock import patch, MagicMock
from asf_tools.ssh.nemo import Nemo


class TestNemoConnection(unittest.TestCase):

    @patch('asf_tools.ssh.nemo.Connection')
    def test_nemo_init_with_key_file(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq", key_file="/path/to/key")
        MockConnection.assert_called_once_with(
            host="login.nemo.thecrick.org",
            user="svc-asf-seq",
            connect_kwargs={"key_filename": "/path/to/key"}
        )
        self.assertIsNotNone(nemo.connection)

    @patch('asf_tools.ssh.nemo.Connection')
    def test_nemo_init_with_password(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq", password="password")
        MockConnection.assert_called_once_with(
            host="login.nemo.thecrick.org",
            user="svc-asf-seq",
            connect_kwargs={"password": "password"}
        )
        self.assertIsNotNone(nemo.connection)

    def test_nemo_init_without_key_or_password(self):
        with self.assertRaises(ValueError):
            Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq")

    @patch('asf_tools.ssh.nemo.Connection')
    def test_nemo_disconnect(self, MockConnection):
        nemo = Nemo(host="login.nemo.thecrick.org", user="svc-asf-seq", password="password")
        nemo.disconnect()
        MockConnection().close.assert_called_once()
        self.assertIsNone(nemo.connection)

    @patch('asf_tools.ssh.nemo.Connection')
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

    # def test_nemo_dev(self):
    #     nemo = Nemo(host="login007.nemo.thecrick.org", user="cheshic", key_file="/Users/cheshic/.ssh/nemo_rsa")
    #     folder = nemo.list_directory("~")

    #     for file in folder:
    #         print(file)

    #     raise NotImplementedError("Test not implemented")
