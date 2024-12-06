"""
Tests for the Storage Interface module.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,invalid-name

import unittest
import pytest
import os
from unittest.mock import patch, MagicMock

from asf_tools.io.storage_interface import InterfaceType, StorageInterface


class TestStorageInterface(unittest.TestCase):

    @patch("os.listdir")
    def test_storage_mock_list_directory_local(self, mock_listdir):
        mock_listdir.return_value = ["file1.txt", "file2.txt", "dir1"]
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        result = storage_interface.list_directory("/some/local/path")
        mock_listdir.assert_called_once_with("/some/local/path")
        self.assertEqual(result, ["file1.txt", "file2.txt", "dir1"])

    @patch("asf_tools.ssh.nemo.Connection")
    def test_storage_mock_list_directory_nemo(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = (
            "total 8\n"
            "drwxr-xr-x 2 user group 4096 2023-10-01 12:34 .\n"
            "drwxr-xr-x 3 user group 4096 2023-10-01 12:34 ..\n"
            "-rw-r--r-- 1 user group 1234 2023-10-01 12:34 test_file.txt\n"
            "lrwxrwxrwx 1 user group 1234 2023-10-01 12:34 link -> target"
        )
        MockConnection().run.return_value = mock_result

        storage_interface = StorageInterface(InterfaceType.NEMO, host="login.nemo.thecrick.org", user="user", password="password")
        result = storage_interface.list_directory("~")

        MockConnection().run.assert_called_once_with("cd ~ && ls -la --time-style=long-iso", hide=True)
        self.assertEqual(result, [".", "..", "test_file.txt", "link"])

    @patch("os.path.exists")
    def test_storage_mock_exists_local(self, mock_exists):
        mock_exists.return_value = True
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        result = storage_interface.exists("/some/local/path")
        mock_exists.assert_called_once_with("/some/local/path")
        self.assertTrue(result)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_storage_mock_exists_nemo(self, MockConnection):
        mock_result = MagicMock()
        mock_result.ok = True
        MockConnection().run.return_value = mock_result

        storage_interface = StorageInterface(InterfaceType.NEMO, host="login.nemo.thecrick.org", user="user", password="password")
        result = storage_interface.exists("~")

        MockConnection().run.assert_called_once_with("test -e ~", hide=True)
        self.assertTrue(result)

    @patch("subprocess.run")
    def test_storage_mock_run_command_local(self, mock_run):
        mock_run.return_value = MagicMock(stdout="command output", stderr="error output")
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        result = storage_interface.run_command("ls -las")
        mock_run.assert_called_once_with("ls -las", shell=True, check=True)
        self.assertIsNotNone(result)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_storage_mock_run_command_nemo(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = "command output"
        mock_result.stderr.strip.return_value = "error output"
        MockConnection().run.return_value = mock_result

        storage_interface = StorageInterface(InterfaceType.NEMO, host="login.nemo.thecrick.org", user="user", password="password")
        stdout, stderr = storage_interface.run_command("ls -las")

        MockConnection().run.assert_called_once_with("ls -las", hide=True)
        self.assertEqual(stdout, "command output")
        self.assertEqual(stderr, "error output")


class TestStorageInterfaceIntegrationTests(unittest.TestCase):

    @pytest.mark.only_run_with_direct_target
    def test_storage_integration_list_directory_local(self):
        # Init
        storage_interface = StorageInterface(InterfaceType.LOCAL)

        # Test
        result = storage_interface.list_directory("./tests/data")

        # Assert
        self.assertTrue("illumina" in result)


    @pytest.mark.only_run_with_direct_target
    def test_storage_integration_list_directory_remote(self):
        # Init
        key_path = os.path.join(os.path.expanduser("~"), ".ssh", "svc_asf")
        storage_interface = StorageInterface(InterfaceType.NEMO, host="login007.nemo.thecrick.org", user="svc-asf-seq", key_file=key_path)
        print(key_path)

        # Test
        result = storage_interface.list_directory(".")

        # Assert
        self.assertTrue("working" in result)
