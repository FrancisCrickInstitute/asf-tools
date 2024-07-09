"""
Tests covering the data_transfer module
"""

import unittest
import tempfile

from click.testing import CliRunner

class TestDataTransfer(unittest.TestCase):
    """Class for data_transfer tests""" 

    def setUp(self):
        self.runner = CliRunner()
        self.tmp_dir = tempfile.mkdtemp()

    def test_clarity_helper_transfer_data(self, api):
        # Set up
        samplesheet = "./tests/data/ont/samplesheet/samplesheet.csv"
        data_path = "./tests/data/ont/runs/run01"
        symlink_data_path = "./tests/data/ont/temp_symlink/"

        # Test
        symlinked_data = api.transfer_data(samplesheet, data_path, symlink_data_path) # shouldn't require api connection, but returns error if api not included

        # Assert
        # Check if symlinks were created (if symlinked path+file exists) then remove symlink
        # temp_location = symlink_data_path + "dummy.txt"
        # assert os.path.exists(temp_location)
        # then remove symlink
        # if assert:
            # unlink temp_location