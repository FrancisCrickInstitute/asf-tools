"""
Tests for the Storage Interface module.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,invalid-name

import os
import unittest
from unittest.mock import MagicMock, patch

import pytest

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

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_storage_mock_list_directories_with_links_local(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = ["dir1", "dir2", "link_to_dir"]
        mock_isdir.side_effect = lambda x: x != "link_to_dir"
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        result = storage_interface.list_directories_with_links("/some/local/path")
        mock_listdir.assert_called_once_with("/some/local/path")
        self.assertEqual(result, ["dir1", "dir2", "link_to_dir"])

    @patch("asf_tools.ssh.nemo.Connection")
    def test_storage_mock_list_directories_with_links_nemo(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = (
            "total 8\n"
            "drwxr-xr-x 2 user group 4096 2023-10-01 12:34 dir1\n"
            "drwxr-xr-x 3 user group 4096 2023-10-01 12:34 dir2\n"
            "lrwxrwxrwx 1 user group 1234 2023-10-01 12:34 link_to_dir -> /some/target/dir"
        )
        MockConnection().run.return_value = mock_result

        storage_interface = StorageInterface(InterfaceType.NEMO, host="login.nemo.thecrick.org", user="user", password="password")
        result = storage_interface.list_directories_with_links("~")

        MockConnection().run.assert_called_once_with("cd ~ && ls -la --time-style=long-iso", hide=True)
        self.assertEqual(result, ["dir1", "dir2", "link_to_dir"])

    @patch("os.path.exists")
    @patch("asf_tools.io.utils.check_file_exist")
    def test_storage_mock_exists_with_pattern_local(self, mock_check_file_exist, mock_exists):
        mock_exists.return_value = True
        mock_check_file_exist.return_value = True
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        result = storage_interface.exists_with_pattern("/some/local/path", "*.txt")
        mock_exists.assert_called_once_with("/some/local/path")
        # mock_check_file_exist.assert_called_once_with("/some/local/path", "*.txt")
        # self.assertTrue(result)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_storage_mock_exists_with_pattern_nemo(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = "test_file.txt"
        MockConnection().run.return_value = mock_result

        storage_interface = StorageInterface(InterfaceType.NEMO, host="login.nemo.thecrick.org", user="user", password="password")
        result = storage_interface.exists_with_pattern("/home/user", "test_file.txt")

        MockConnection().run.assert_called_once_with("find /home/user -maxdepth 1 -name 'test_file.txt'", hide=True)
        self.assertTrue(result)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_storage_mock_make_dirs_nemo(self, MockConnection):
        storage_interface = StorageInterface(InterfaceType.NEMO, host="login.nemo.thecrick.org", user="user", password="password")
        storage_interface.make_dirs("/some/new/directory")
        MockConnection().run.assert_called_once_with("mkdir -p /some/new/directory", hide=True)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_storage_mock_write_file_nemo(self, MockConnection):
        storage_interface = StorageInterface(InterfaceType.NEMO, host="login.nemo.thecrick.org", user="user", password="password")
        storage_interface.write_file("/some/path/to/file.txt", "file content")
        MockConnection().run.assert_called_once_with('echo "file content" > /some/path/to/file.txt', hide=True)

    @patch("asf_tools.ssh.nemo.Connection")
    def test_storage_mock_read_file_nemo(self, MockConnection):
        mock_result = MagicMock()
        mock_result.stdout.strip.return_value = "file content"
        MockConnection().run.return_value = mock_result

        storage_interface = StorageInterface(InterfaceType.NEMO, host="login.nemo.thecrick.org", user="user", password="password")
        content = storage_interface.read_file("/some/path/to/file.txt")

        MockConnection().run.assert_called_once_with("cat /some/path/to/file.txt", hide=True)
        self.assertEqual(content, "file content")

    def test_storage_parse_permission_string(self):
        storage_interface = StorageInterface(InterfaceType.LOCAL)

        perm, numeric_perm = storage_interface.parse_permission_string("rwxr-xr--")
        self.assertEqual(perm, 0o754)
        self.assertEqual(numeric_perm, "754")

        perm, numeric_perm = storage_interface.parse_permission_string("rw-rw-r--")
        self.assertEqual(perm, 0o664)
        self.assertEqual(numeric_perm, "664")

        with self.assertRaises(ValueError):
            storage_interface.parse_permission_string("invalid")

    @patch("asf_tools.ssh.nemo.Connection")
    def test_storage_mock_chmod_nemo(self, MockConnection):
        storage_interface = StorageInterface(InterfaceType.NEMO, host="login.nemo.thecrick.org", user="user", password="password")
        storage_interface.chmod("/some/path/to/file.txt", "rwxr-xr--")
        MockConnection().run.assert_called_once_with("chmod 754 /some/path/to/file.txt", hide=True)

    @patch("os.chmod")
    def test_storage_mock_chmod_local(self, mock_chmod):
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        storage_interface.chmod("/some/path/to/file.txt", "rwxr-xr--")
        mock_chmod.assert_called_once_with("/some/path/to/file.txt", 0o754)


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
