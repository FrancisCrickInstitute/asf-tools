"""
Tests covering the data_transfer module
"""

import os
import unittest

from asf_tools.io.data_management import DataManagement

from .utils import with_temporary_folder


class TestDataManagement(unittest.TestCase):
    """Class for data_management tests"""

    @with_temporary_folder
    def test_symlink_to_target_isinvalid_source(self, tmp_path):
        """
        Check existence of input path
        """

        # Set up
        dt = DataManagement()
        invalid_path = os.path.join(tmp_path, "invalid")

        # Test and Assert
        with self.assertRaises(FileNotFoundError):
            dt.symlink_to_target(invalid_path, tmp_path)

    @with_temporary_folder
    def test_symlink_to_target_isinvalid_target(self, tmp_path):
        """
        Check existence of target path
        """

        # Set up
        dt = DataManagement()
        valid_path = "./tests/data/ont/runs/run01"
        invalid_path = os.path.join(tmp_path, "invalid")

        # Test and Assert
        with self.assertRaises(FileNotFoundError):
            dt.symlink_to_target(valid_path, invalid_path)

    @with_temporary_folder
    def test_symlink_to_target_isvalid_str(self, tmp_path):
        """
        Check folder has been symlinked correctly
        """

        # Set up
        dt = DataManagement()
        data_path = "tests/data/ont/runs/run01/"

        # Test
        dt.symlink_to_target(data_path, tmp_path)

        # Assert
        run_dir_1 = os.path.join(tmp_path, "run01")
        self.assertTrue(os.path.islink(run_dir_1))

    @with_temporary_folder
    def test_symlink_to_target_isvalid_list(self, tmp_path):
        """
        Check folder has been symlinked correctly
        """

        # Set up
        dt = DataManagement()
        data_path = "tests/data/ont/runs/run01/"

        # Create list of temporary paths
        tmp_path1 = os.path.join(tmp_path, "test1")
        tmp_path2 = os.path.join(tmp_path, "test2")
        tmp_paths = [tmp_path1, tmp_path2]
        # Create directories if they do not exist
        os.makedirs(tmp_path1, exist_ok=True)
        os.makedirs(tmp_path2, exist_ok=True)

        # Test
        dt.symlink_to_target(data_path, tmp_paths)

        # Assert
        run_dir_1 = os.path.join(tmp_path1, "run01")
        run_dir_2 = os.path.join(tmp_path2, "run01")
        self.assertTrue(os.path.islink(run_dir_1))
        self.assertTrue(os.path.islink(run_dir_2))
