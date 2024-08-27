"""
Tests for io util functions
"""

import os

from unittest import mock
from unittest.mock import MagicMock, patch

from asf_tools.io.utils import check_file_exist, list_directory_names, delete_all_items

from ..utils import with_temporary_folder


def test_list_directory(self):
    """Test list directories"""

    # Setup
    path = "tests/data/ont/runs"

    # Test
    dir_list = list_directory_names(path)

    # Assert
    self.assertEqual(len(dir_list), 3)


@with_temporary_folder
def test_list_directory_symlink(self, tmp_path):
    """Test list directories"""

    # Setup
    path = "tests/data/ont/runs"

    # Create symlinks
    for entry in os.listdir(path):
        source_path = os.path.join(path, entry)
        if os.path.isdir(source_path):
            symlink_path = os.path.join(tmp_path, entry)
            os.symlink(source_path, symlink_path)

    # Test
    dir_list = list_directory_names(tmp_path)

    # Assert
    self.assertEqual(len(dir_list), 3)


def test_check_file_exist_isvalid(self):
    """Test if different paths return a boolean value as expected"""

    # Setup
    path1 = "tests/data/ont/runs/run01"
    path2 = "tests/data/ont/runs/run02"
    path3 = "tests/data/ont/runs/run03"
    pattern = "sequencing_summary*"

    # Test
    run1 = check_file_exist(path1, pattern)
    run2 = check_file_exist(path2, pattern)
    run3 = check_file_exist(path3, pattern)

    # Assert
    self.assertTrue(run1)
    self.assertTrue(run2)
    self.assertFalse(run3)


def test_check_file_exist_invalid(self):
    """Test path returns false"""

    # Setup
    path1 = "tests/data/ont/runs/run03"
    pattern = "sequencing_summary*"

    # Test
    run = check_file_exist(path1, pattern)

    # Assert
    self.assertFalse(run)


def test_check_file_exist_pathnotexist(self):
    """Test if different paths return true/false as expected"""

    # Setup
    path1 = "path/not/valid"
    pattern = "pattern"

    # Test and Assert
    with self.assertRaises(FileNotFoundError):
        check_file_exist(path1, pattern)

def test_delete_all_items_valid_pathnotexist(self):
    """Test a non existant path"""

    # Setup
    path1 = "path/not/valid"
    pattern = "files_in_dir"

    # Test and Assert
    with self.assertRaises(FileNotFoundError):
        delete_all_items(path1, pattern)

def test_delete_all_items_valid_mode_invalid(self):
    """Test an invalid mode"""

    # Setup
    path1 = "tests/data/ont/runs/run01"
    mode = "pattern"

    # Test and Assert
    with self.assertRaises(ValueError):
        delete_all_items(path1, mode)

def test_delete_all_items_valid_filemode(self):
    """Test deletion of files on a top level"""

    # Set up
    path = "tests/data/ont/runs/run01"

    # mock os.path.isdir, os.walk, and os.remove
    with patch('os.path.isdir', return_value=True) as mock_isdir, \
         patch('os.walk', return_value=[(path, [], ["file1.txt", "file2.txt"])]) as mock_walk, \
         patch('os.remove') as mock_remove:

        # Test
        delete_all_items(path, "files_in_dir")

        # Assert
        # check that os.path.isdir was called with the correct path
        mock_isdir.assert_called_once_with(path)
        # check that os.walk was called with the correct path
        mock_walk.assert_called_once_with(path)
        # check that os.remove was called for each file
        mock_remove.assert_any_call(os.path.join(path, "file1.txt"))
        mock_remove.assert_any_call(os.path.join(path, "file2.txt"))

def test_delete_all_items_valid_dirmode(mock_os):
    """Test deletion of files within dirs"""

    path = "tests/data/ont/runs/run01"
    mode = "dir_tree"

    # Use patch to mock os.path.isdir and shutil.rmtree
    with patch('os.path.isdir', return_value=True) as mock_isdir, \
         patch('shutil.rmtree') as mock_rmtree:

        # Test
        delete_all_items(path, mode)

        # Assert
        # check that os.path.isdir was called once with the correct path
        mock_isdir.assert_called_once_with(path)
        # check that shutil.rmtree was called once with the correct path
        mock_rmtree.assert_called_once_with(path)
