"""
Tests for the data transfer class
"""

import os

from asf_tools.io.data_management import DataManagement

from .utils import check_file_exist, with_temporary_folder


# @with_temporary_folder
# def test_symlink_to_target_isinvalid_source(self, tmp_path):
#     """
#     Check existence of input path
#     """

#     # Set up
#     dt = DataManagement()
#     invalid_path = os.path.join(tmp_path, "invalid")

#     # Test and Assert
#     with self.assertRaises(FileNotFoundError):
#         dt.symlink_to_target(invalid_path, tmp_path)


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
    run_dir_1 = os.path.join(tmp_path1, "asf", "DN20049", "201008_K00371_0409_BHHY7WBBXY")
    run_dir_2 = os.path.join(tmp_path2, "asf", "RN20066", "201008_K00371_0409_BHHY7WBBXY")
    run_dir_3 = os.path.join(tmp_path3, "asf", "SC19230", "201008_K00371_0409_BHHY7WBBXY")
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


@with_temporary_folder
def test_deliver_to_targets_symlink_overide(self, tmp_path):
    """
    Test Symlink override
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
    dt.deliver_to_targets(basepath_target, tmp_path, "/test/path")

    # Assert
    run_dir_1 = os.path.join(tmp_path1, "asf", "DN20049", "201008_K00371_0409_BHHY7WBBXY")
    run_dir_2 = os.path.join(tmp_path2, "asf", "RN20066", "201008_K00371_0409_BHHY7WBBXY")
    run_dir_3 = os.path.join(tmp_path3, "asf", "SC19230", "201008_K00371_0409_BHHY7WBBXY")
    self.assertTrue(os.path.islink(run_dir_1))
    self.assertTrue(os.path.islink(run_dir_2))
    self.assertTrue(os.path.islink(run_dir_3))

    link = os.readlink(run_dir_1)
    self.assertTrue("/test/path" in link)


def test_check_pipeline_run_complete_false(self):
    """
    Test function when the pipeline run is not complete
    """

    # Set up
    dm = DataManagement()
    run_dir = "tests/data/ont/runs/run01"

    # Test
    result = dm.check_pipeline_run_complete(run_dir)

    # Assert
    self.assertFalse(result)


def test_check_pipeline_run_complete_true(self):
    """
    Test function when the pipeline run is complete
    """

    # Set up
    dm = DataManagement()
    run_dir = "tests/data/ont/complete_pipeline_outputs/complete_run_01"

    # Test
    result = dm.check_pipeline_run_complete(run_dir)

    # Assert
    self.assertTrue(result)


def test_scan_delivery_state_source_invalid(self):
    """
    Test function when the source path doesn't exist
    """

    # Set up
    dm = DataManagement()
    source_dir = "fake/path/"
    target_dir = "tests/data/ont/live_runs/pipeline_output"

    # Test and Assert
    with self.assertRaises(FileNotFoundError):
        dm.scan_delivery_state(source_dir, target_dir)


def test_scan_delivery_state_target_invalid(self):
    """
    Test function when the target path doesn't exist
    """

    # Set up
    dm = DataManagement()
    source_dir = "tests/data/ont/runs/run01"
    target_dir = "fake/path/"

    # Test and Assert
    with self.assertRaises(FileNotFoundError):
        dm.scan_delivery_state(source_dir, target_dir)


@with_temporary_folder
def test_scan_delivery_state_all_to_deliver(self, tmp_path):
    """
    Test function when all data is to be delivered
    """

    # Set up
    tmp_path1 = os.path.join(tmp_path, "swantonc")
    os.makedirs(tmp_path1)
    dm = DataManagement()
    source_dir = "tests/data/ont/complete_pipeline_outputs"
    target_dir = tmp_path

    # Test
    result = dm.scan_delivery_state(source_dir, target_dir)

    # Assert
    self.assertEqual(len(result), 2)


@with_temporary_folder
def test_scan_delivery_state_partial_to_deliver(self, tmp_path):
    """
    Test function when all data is to be delivered
    """

    # Set up
    tmp_path1 = os.path.join(tmp_path, "swantonc")
    os.makedirs(tmp_path1)
    dm = DataManagement()
    source_dir = "tests/data/ont/complete_pipeline_outputs"
    target_dir = tmp_path
    dm.deliver_to_targets(source_dir + "/complete_run_01/results/grouped", tmp_path)

    # Test
    result = dm.scan_delivery_state(source_dir, target_dir)

    # Assert
    self.assertEqual(len(result), 1)


@with_temporary_folder
def test_scan_delivery_state_none_to_deliver(self, tmp_path):
    """
    Test function when all data is to be delivered
    """

    # Set up
    tmp_path1 = os.path.join(tmp_path, "swantonc")
    os.makedirs(tmp_path1)
    dm = DataManagement()
    source_dir = "tests/data/ont/complete_pipeline_outputs"
    target_dir = tmp_path
    dm.deliver_to_targets(source_dir + "/complete_run_01/results/grouped", tmp_path)
    dm.deliver_to_targets(source_dir + "/complete_run_02/results/grouped", tmp_path)

    # Test
    result = dm.scan_delivery_state(source_dir, target_dir)

    # Assert
    self.assertEqual(len(result), 0)


def test_data_to_archive():
    """
    Test function when the source path has dirs older than 1 hr
    """

    # Set up
    dm = DataManagement()
    data_path = "tests/data/ont/runs"
    archived = []
    for root, dirs, files in os.walk(data_path):  # pylint: disable=unused-variable
        for dir_name in dirs:
            if check_file_exist(dir_name, "archived_data"):
                archived.extend(dir_name)

    # Test
    # Return dirs that are older than 1 hr
    old_data = dm.data_to_archive(data_path, 0.00137)
    print(old_data)

    # Assert
    for dir_path in archived:
        assert dir_path not in old_data
    #     self.assertNotIn(dir_path, old_data)
    assert old_data == {"tests/data/ont/runs/run01": "August 15, 2024, 10:09:38 UTC", "tests/data/ont/runs/run02": "August 15, 2024, 10:09:38 UTC"}


def test_test_data_to_archive_noolddir():
    """
    Test function when the target path is newer than set time
    """

    # Set up
    dm = DataManagement()
    data_path = "tests/data/ont/runs"

    # Test
    # Return dirs that are older than 1000 months
    old_data = dm.data_to_archive(data_path, 1000)

    # Assert
    assert not old_data


def test_test_data_to_archive_nodirs():
    """
    Test function when the target path has no sub-directories
    """

    # Set up
    dm = DataManagement()
    data_path = "tests/data/ont/runs/run01"

    # Test
    old_data = dm.data_to_archive(data_path, 10)

    # Assert
    assert not old_data
