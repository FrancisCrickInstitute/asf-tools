"""
Tests covering the data_transfer module
"""

import unittest
import os
import subprocess

from asf_tools.ont.data_transfer import DataTransfer
from .utils import with_temporary_folder


class TestDataTransfer(unittest.TestCase):
    """Class for data_transfer tests"""

    @with_temporary_folder
    def test_data_transfer_isinvalid_source(self, tmp_path):

        # Set up
        dt = DataTransfer()
        invalid_path = os.path.join(tmp_path, "invalid")

        # Test and Assert
        with self.assertRaises(FileNotFoundError):
            dt.data_transfer(invalid_path, tmp_path)

    @with_temporary_folder
    def test_data_transfer_isinvalid_target(self, tmp_path):

        # Set up
        dt = DataTransfer()
        valid_path = "./tests/data/ont/runs/run01"
        invalid_path = os.path.join(tmp_path, "invalid")

        # Test and Assert
        with self.assertRaises(FileNotFoundError):
            dt.data_transfer(valid_path, invalid_path)

    @with_temporary_folder
    def test_data_transfer_isvalid(self, tmp_path):

        # Set up
        dt = DataTransfer()
        data_path = "tests/data/ont/runs/run01/"

        # Test
        dt.data_transfer(data_path, tmp_path)

        # Assert
        run_dir_1 = os.path.join(tmp_path, "run01")
        subprocess.run(f"ls -la {tmp_path}", shell=True, check=True)
        # print(tmp_path)
        # print(run_dir_1)
        # print(os.path.exists(run_dir_1))
        # print(f"Contents of tmp_path: {os.listdir(tmp_path)}")
        print(f"Contents of tmp_path: {os.path.islink(run_dir_1)}")  # returns true
        self.assertTrue(os.path.exists(run_dir_1))

        # # Set up
        # samplesheet = "./tests/data/ont/samplesheet/samplesheet.csv"
        # data_path = "./tests/data/ont/runs/run01"
        # symlink_data_path = "./tests/data/ont/temp_symlink/"

        # # Test
        # symlinked_data = api.data_transfer(samplesheet, data_path, symlink_data_path) # shouldn't require api connection, but returns error if api not included

        # # Assert
        # # Check if symlinks were created (if symlinked path+file exists) then remove symlink
        # # temp_location = symlink_data_path + "dummy.txt"
        # # assert os.path.exists(temp_location)
        # # then remove symlink
        # # if assert:
        #     # unlink temp_location
