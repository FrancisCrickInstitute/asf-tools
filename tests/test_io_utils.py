"""
Tests for io util functions
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

import os

from assertpy import assert_that

from asf_tools.io.utils import DeleteMode, check_file_exist, delete_all_items, list_directory_names


class TestIoUtils:
    """Class for testing the io utils"""

    def test_list_directory(self):
        """Test list directories"""

        # Setup
        path = "tests/data/ont/runs"

        # Test and assert
        assert_that(len(list_directory_names(path))).is_equal_to(5)

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
        assert_that(len(dir_list)).is_equal_to(5)

    def test_check_file_exist_isvalid(self):
        """Test if different paths return a boolean value as expected"""

        # Setup
        path1 = "tests/data/ont/runs/run01"
        path2 = "tests/data/ont/runs/run02"
        path3 = "tests/data/ont/runs/run03"
        pattern = "sequencing_summary*"

        # Test and Assert
        assert_that(check_file_exist(path1, pattern)).is_true()
        assert_that(check_file_exist(path2, pattern)).is_true()
        assert_that(check_file_exist(path3, pattern)).is_false()

    def test_check_file_exist_invalid(self):
        """Test path returns false"""

        # Setup
        path1 = "tests/data/ont/runs/run03"
        pattern = "sequencing_summary*"

        # Test and assert
        assert_that(check_file_exist(path1, pattern)).is_false()

    def test_check_file_exist_pathnotexist(self):
        """Test if different paths return true/false as expected"""

        # Setup
        path1 = "path/not/valid"
        pattern = "pattern"

        # Test and Assert
        assert_that(check_file_exist).raises(FileNotFoundError).when_called_with(path1, pattern)

    def test_delete_all_items_valid_pathnotexist(self):
        """Test a non existant path"""

        # Setup
        path1 = "path/not/valid"
        pattern = DeleteMode.FILES_IN_DIR

        # Test and Assert
        assert_that(delete_all_items).raises(FileNotFoundError).when_called_with(path1, pattern)

    def test_delete_all_items_valid_mode_invalid(self, tmp_path):
        """Test an invalid mode"""

        # Setup
        mode = "pattern"

        # Test and Assert
        assert_that(delete_all_items).raises(ValueError).when_called_with(tmp_path, mode)

    def test_delete_all_items_valid_filemode(self, tmp_path):
        """Test deletion of files within dirs"""

        # Set up
        mode = DeleteMode.FILES_IN_DIR

        # create dir and file structure
        test_file = os.path.join(tmp_path, "dummy.txt")
        with open(test_file, "w", encoding="utf-8"):
            pass

        subdir = os.path.join(tmp_path, "subdir")
        os.makedirs(subdir)
        test_subdir_file = os.path.join(subdir, "dummy.txt")
        with open(test_subdir_file, "w", encoding="utf-8"):
            pass

        assert_that(os.path.isfile(test_file)).is_true()
        assert_that(os.path.isfile(test_subdir_file)).is_true()

        # Test
        delete_all_items(tmp_path, mode)

        # Assert
        assert_that(os.path.isfile(test_file)).is_false()

    def test_delete_all_items_valid_dirmode(self, tmp_path):
        """Test deletion of all items within specific dir"""

        # Set up
        mode = DeleteMode.DIR_TREE

        # create dir and file structure
        work_dir = os.path.join(tmp_path, "work")
        os.makedirs(work_dir)
        test_file = os.path.join(work_dir, "dummy.txt")
        with open(test_file, "w", encoding="utf-8"):
            pass

        subdir = os.path.join(work_dir, "subdir")
        os.makedirs(subdir)
        test_subdir_file = os.path.join(subdir, "dummy.txt")
        with open(test_subdir_file, "w", encoding="utf-8"):
            pass

        assert_that(os.path.isfile(test_file)).is_true()
        assert_that(os.path.isfile(test_subdir_file)).is_true()

        # Test
        delete_all_items(work_dir, mode)

        # Assert
        assert_that(os.path.isfile(test_file)).is_false()
        assert_that(os.path.isfile(test_subdir_file)).is_false()
