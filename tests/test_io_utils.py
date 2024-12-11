"""
Tests for io util functions
"""

import os
import unittest

from asf_tools.io.utils import DeleteMode, check_file_exist, delete_all_items, list_directory_names

from tests.utils import with_temporary_folder


class TestIOUtils(unittest.TestCase):
    def test_io_utils_list_directory(self):
        """Test list directories"""

        # Setup
        path = "tests/data/ont/runs"

        # Test
        dir_list = list_directory_names(path)

        # Assert
        self.assertEqual(len(dir_list), 3)


    @with_temporary_folder
    def test_io_utils_list_directory_symlink(self, tmp_path):
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


    def test_io_utils_check_file_exist_isvalid(self):
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


    def test_io_utils_check_file_exist_invalid(self):
        """Test path returns false"""

        # Setup
        path1 = "tests/data/ont/runs/run03"
        pattern = "sequencing_summary*"

        # Test
        run = check_file_exist(path1, pattern)

        # Assert
        self.assertFalse(run)


    def test_io_utils_check_file_exist_pathnotexist(self):
        """Test if different paths return true/false as expected"""

        # Setup
        path1 = "path/not/valid"
        pattern = "pattern"

        # Test and Assert
        with self.assertRaises(FileNotFoundError):
            check_file_exist(path1, pattern)


    def test_io_utils_delete_all_items_valid_pathnotexist(self):
        """Test a non existant path"""

        # Setup
        path1 = "path/not/valid"
        pattern = DeleteMode.FILES_IN_DIR

        # Test and Assert
        with self.assertRaises(FileNotFoundError):
            delete_all_items(path1, pattern)


    @with_temporary_folder
    def test_io_utils_delete_all_items_valid_mode_invalid(self, tmp_path):
        """Test an invalid mode"""

        # Setup
        mode = "pattern"

        # Test and Assert
        with self.assertRaises(ValueError):
            delete_all_items(tmp_path, mode)


    @with_temporary_folder
    def test_io_utils_delete_all_items_valid_filemode(self, tmp_path):
        """Test deletion of files within dirs"""

        # Set up
        mode = DeleteMode.FILES_IN_DIR

        # create dir and file structure
        test_io_utils_file = os.path.join(tmp_path, "dummy.txt")
        with open(test_io_utils_file, "w", encoding="utf-8"):
            pass

        subdir = os.path.join(tmp_path, "subdir")
        os.makedirs(subdir)
        test_io_utils_subdir_file = os.path.join(subdir, "dummy.txt")
        with open(test_io_utils_subdir_file, "w", encoding="utf-8"):
            pass

        self.assertTrue(os.path.isfile(test_io_utils_file))
        self.assertTrue(os.path.isfile(test_io_utils_subdir_file))

        # Test
        delete_all_items(tmp_path, mode)

        # Assert
        self.assertFalse(os.path.isfile(test_io_utils_file))


    @with_temporary_folder
    def test_io_utils_delete_all_items_valid_dirmode(self, tmp_path):
        """Test deletion of all items within specific dir"""

        # Set up
        mode = DeleteMode.DIR_TREE

        # create dir and file structure
        work_dir = os.path.join(tmp_path, "work")
        os.makedirs(work_dir)
        test_io_utils_file = os.path.join(work_dir, "dummy.txt")
        with open(test_io_utils_file, "w", encoding="utf-8"):
            pass

        subdir = os.path.join(work_dir, "subdir")
        os.makedirs(subdir)
        test_io_utils_subdir_file = os.path.join(subdir, "dummy.txt")
        with open(test_io_utils_subdir_file, "w", encoding="utf-8"):
            pass

        self.assertTrue(os.path.isfile(test_io_utils_file))
        self.assertTrue(os.path.isfile(test_io_utils_subdir_file))

        # Test
        delete_all_items(work_dir, mode)

        # Assert
        self.assertFalse(os.path.isfile(test_io_utils_file))
        self.assertFalse(os.path.isfile(test_io_utils_subdir_file))
