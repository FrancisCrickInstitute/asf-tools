"""
Tests for io util functions
"""

import os

from asf_tools.io.utils import check_file_exist, list_directory_names

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
