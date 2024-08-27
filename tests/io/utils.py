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
    path = "tests/data/io"
    mode = "files_in_dir"

    # create file structure
    test_file = os.path.join(path, "dummy.txt")
    if not os.path.exists(test_file):
        with open(test_file, "w") as file:
            pass
    self.assertTrue(os.path.isfile(test_file))

    # Test
    delete_all_items(path, mode)

    # Assert
    self.assertFalse(os.path.isfile(test_file))

def test_delete_all_items_valid_dirmode(self):
    """Test deletion of files within dirs"""

    path = "tests/data/ont/runs/run01"
    mode = "dir_tree"

    # create dir and file structure
    test_file = os.path.join(path, "dummy.txt")
    if not os.path.exists(test_file):
        with open(test_file, "w") as file:
            pass
    subdir = os.path.join(path, "subdir")
    os.makedirs(subdir)
    test_subdir_file = os.path.join(subdir, "dummy.txt")
    if not os.path.exists(test_subdir_file):
        with open(test_subdir_file, "w") as file:
            pass
    self.assertTrue(os.path.isfile(test_file))
    self.assertTrue(os.path.isfile(test_subdir_file))

    # Test
    delete_all_items(path, mode)

    # Assert
    self.assertFalse(os.path.isfile(test_file))
    self.assertFalse(os.path.isfile(test_subdir_file))
