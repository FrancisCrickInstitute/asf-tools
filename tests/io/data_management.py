"""
Tests for the data transfer class
"""

import os

from asf_tools.io.data_management import DataManagement

from .utils import with_temporary_folder


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

@with_temporary_folder
def test_deliver_to_targets_valid(self, tmp_path):
    """
    Check folders has been symlinked correctly
    """

    # Set up
    dt = DataManagement()
    basepath_target = "tests/data/ont/live_runs/pipeline_output"

    # tmp_path = "/Users/elezia/dev/test_data/asf-tools/pytest"
    tmp_path1 = os.path.join(tmp_path, "swantonc", "nnennaya.kanu")
    tmp_path2 = os.path.join(tmp_path, "ogarraa", "marisol.alvarez-martinez")
    tmp_path3 = os.path.join(tmp_path, "ogarraa", "richard.hewitt")
    os.makedirs(tmp_path1)
    os.makedirs(tmp_path2)
    os.makedirs(tmp_path3)

    # Test
    dt.deliver_to_targets(basepath_target, tmp_path)

    # Assert
    run_dir_1 = os.path.join(tmp_path1, "DN20049", "201008_K00371_0409_BHHY7WBBXY")
    run_dir_2 = os.path.join(tmp_path2, "RN20066", "201008_K00371_0409_BHHY7WBBXY")
    run_dir_3 = os.path.join(tmp_path3, "SC19230", "201008_K00371_0409_BHHY7WBBXY")
    self.assertTrue(os.path.islink(run_dir_1))
    self.assertTrue(os.path.islink(run_dir_2))
    self.assertTrue(os.path.islink(run_dir_3))

@with_temporary_folder
def test_deliver_to_targets_no_user(self, tmp_path):
    """
    Test function when the user path doesn't exist
    """

    # Set up
    dt = DataManagement()
    basepath_target = "tests/data/ont/live_runs/pipeline_output"

    # Test and Assert
    with self.assertRaises(FileNotFoundError):
        dt.deliver_to_targets(basepath_target, tmp_path)

@with_temporary_folder
def test_deliver_to_targets_source_invalid(self, tmp_path):
    """
    Test function when the user path doesn't exist
    """

    # Set up
    dt = DataManagement()
    basepath_target = "fake/path/"

    # Test and Assert
    with self.assertRaises(FileNotFoundError):
        dt.deliver_to_targets(basepath_target, tmp_path)
