"""
Tests for the data transfer class
"""

import os
from datetime import datetime, timezone
from unittest import mock
from unittest.mock import MagicMock, patch

from asf_tools.io.data_management import DataManagement

from .utils import with_temporary_folder


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


def test_check_ont_sequencing_run_complete_false(self):
    """
    Test function when the ONT sequencing run is not complete
    """

    # Set up
    dm = DataManagement()
    run_dir = "tests/data/ont/runs/run03"

    # Test
    result = dm.check_ont_sequencing_run_complete(run_dir)

    # Assert
    self.assertFalse(result)


def test_check_ont_sequencing_run_complete_true(self):
    """
    Test function when the ONT sequencing run is complete
    """

    # Set up
    dm = DataManagement()
    run_dir = "tests/data/ont/runs/run01"

    # Test
    result = dm.check_ont_sequencing_run_complete(run_dir)

    # Assert
    self.assertTrue(result)


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


@patch("asf_tools.slurm.utils.subprocess.run")
def test_scan_run_state_valid(self, mock_run):
    """
    Test scan run state with a valid configuration
    """

    # Set up
    dm = DataManagement()
    raw_dir = "tests/data/ont/end_to_end_example/01_ont_raw"
    run_dir = "tests/data/ont/end_to_end_example/02_ont_run"
    target_dir = "tests/data/ont/end_to_end_example/03_ont_delivery"

    with open("tests/data/slurm/squeue/fake_job_report.txt", "r", encoding="UTF-8") as file:
        mock_output = file.read()
    mock_run.return_value = MagicMock(stdout=mock_output)

    # Test
    data = dm.scan_run_state(raw_dir, run_dir, target_dir, "scan", "asf_nanopore_demux_")

    # Assert
    target_dict = {
        # 'run_01': {'status': 'delivered'},
        "run_02": {"status": "ready_to_deliver"},
        "run_03": {"status": "pipeline_running"},
        "run_04": {"status": "pipeline_pending"},
        "run_05": {"status": "sequencing_complete"},
        "run_06": {"status": "sequencing_in_progress"},
    }
    self.assertEqual(data, target_dict)


@mock.patch("asf_tools.io.data_management.os.walk")
@mock.patch("asf_tools.io.data_management.os.path.getmtime")
@mock.patch("asf_tools.io.data_management.check_file_exist")
@mock.patch("asf_tools.io.data_management.datetime")
@with_temporary_folder
def test_find_stale_directories_valid(self, mock_datetime, mock_check_file_exist, mock_getmtime, mock_walk, tmp_path):
    """
    Test function when the with mocked, older paths
    """

    # Set Up
    # create path structure
    dir1 = os.path.join(tmp_path, "dir1")
    dir2 = os.path.join(tmp_path, "dir2")
    os.makedirs(dir1)
    os.makedirs(dir2)

    # mock current time
    fixed_current_time = datetime(2024, 8, 15, tzinfo=timezone.utc)
    mock_datetime.now.return_value = fixed_current_time
    mock_datetime.fromtimestamp = datetime.fromtimestamp

    # setup mock return values
    mock_walk.return_value = [
        (tmp_path, ["dir1", "dir2"], []),
    ]
    mock_getmtime.side_effect = lambda path: datetime(2024, 6, 15, tzinfo=timezone.utc).timestamp()  # time older than threshold
    mock_check_file_exist.side_effect = lambda path, flag: False

    # Test
    dm = DataManagement()
    result = dm.find_stale_directories(tmp_path, 2)

    # Assert the result

    expected_result = {
        "dir1": {
            "path": dir1,
            "days_since_modified": 61,
            "last_modified_h": "June 15, 2024, 00:00:00 UTC",
            "last_modified_m": "2024-06-15 00:00:00+00:00",
        },
        "dir2": {
            "path": dir2,
            "days_since_modified": 61,
            "last_modified_h": "June 15, 2024, 00:00:00 UTC",
            "last_modified_m": "2024-06-15 00:00:00+00:00",
        },
    }
    self.assertEqual(result, expected_result)


@with_temporary_folder
def test_find_stale_directories_with_modified_files_in_dir(self, tmp_path):
    """
    Test function with directories that have files affecting the modification time.
    This test uses a temporary folder and mocks editing times.
    """

    # Set Up
    # create path structure
    dir1 = os.path.join(tmp_path, "dir1")
    os.makedirs(dir1)
    file1 = os.path.join(dir1, "file1.txt")
    with open(file1, "w", encoding="utf-8") as f:
        f.write("test file")

    # set up mock structure
    with (
        mock.patch("asf_tools.io.data_management.os.walk") as mock_walk,
        mock.patch("asf_tools.io.data_management.os.path.getmtime") as mock_getmtime,
        mock.patch("asf_tools.io.data_management.check_file_exist") as mock_check_file_exist,
        mock.patch("asf_tools.io.data_management.datetime") as mock_datetime,
    ):

        fixed_current_time = datetime(2024, 8, 15, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_current_time
        mock_datetime.fromtimestamp = datetime.fromtimestamp

        mock_walk.return_value = [
            (tmp_path, ["dir1"], []),
            (dir1, [], ["file1.txt"]),
        ]
        mock_getmtime.side_effect = lambda path: {
            file1: datetime(2024, 5, 15, tzinfo=timezone.utc).timestamp(),
            dir1: datetime(2024, 6, 15, tzinfo=timezone.utc).timestamp(),
        }.get(path, datetime(2024, 6, 15, tzinfo=timezone.utc).timestamp())
        mock_check_file_exist.side_effect = lambda path, flag: False

        # Test
        dm = DataManagement()
        result = dm.find_stale_directories(tmp_path, 2)

        # Assert the result
        expected_result = {
            "dir1": {
                "path": dir1,
                "days_since_modified": 61,
                "last_modified_h": "June 15, 2024, 00:00:00 UTC",
                "last_modified_m": "2024-06-15 00:00:00+00:00",
            },
        }
        self.assertEqual(result, expected_result)


@mock.patch("asf_tools.io.data_management.os.path.getmtime")
@mock.patch("asf_tools.io.data_management.datetime")
def test_find_stale_directories_with_archived_dirs(self, mock_datetime, mock_getmtime):  # pylint: disable=unused-variable
    """
    Test function with real directories and return all dirs except those with an "archive_readme.txt" file
    This test uses real folders and mocks editing times.
    """

    # Set Up
    fixed_current_time = datetime(2024, 8, 15, tzinfo=timezone.utc)
    mock_datetime.now.return_value = fixed_current_time
    mock_datetime.fromtimestamp = datetime.fromtimestamp
    mock_getmtime.side_effect = lambda path: datetime(2024, 6, 15, tzinfo=timezone.utc).timestamp()

    # Test
    dm = DataManagement()
    old_data = dm.find_stale_directories("tests/data/ont/runs", 2)
    print(old_data)

    # Assert
    expected_results = {
        "run01": {
            "path": "tests/data/ont/runs/run01",
            "days_since_modified": 61,
            "last_modified_h": "June 15, 2024, 00:00:00 UTC",
            "last_modified_m": "2024-06-15 00:00:00+00:00",
        },
        "run02": {
            "path": "tests/data/ont/runs/run02",
            "days_since_modified": 61,
            "last_modified_h": "June 15, 2024, 00:00:00 UTC",
            "last_modified_m": "2024-06-15 00:00:00+00:00",
        },
    }
    assert old_data == expected_results


def test_find_stale_directories_noolddir(self):  # pylint: disable=unused-variable
    """
    Test function when the target path is newer than set time
    """

    # Set up
    dm = DataManagement()
    data_path = "tests/data/ont/runs"

    # Test
    # Return dirs that are older than 1000 months
    old_data = dm.find_stale_directories(data_path, 1000)

    # Assert
    assert not old_data


def test_find_stale_directories_nodirs(self):
    """
    Test function when the target path has no sub-directories
    """

    # Set Up
    dm = DataManagement()
    data_path = "invalid/test/path"

    # Test and Assert
    with self.assertRaises(FileNotFoundError):
        dm.find_stale_directories(data_path, 2)


@mock.patch("asf_tools.io.data_management.os.path.getmtime")
@mock.patch("asf_tools.io.data_management.datetime")
def test_pipeline_cleaning_workdir_valid(self, mock_datetime, mock_getmtime):
    """
    Test function with directories that have a mock editing time.
    Creates work directories and checks correct deletion of work dir.
    """
    # Set Up
    dm = DataManagement()
    data_path = "tests/data/ont/runs"
    for root, dirs, files in os.walk(data_path):  # pylint: disable=unused-variable
        if root == data_path:
            for directory in dirs:
                work_dir = os.path.join(root, directory, "work")
                if not os.path.exists(work_dir):
                    os.makedirs(work_dir)

    # set up mock structure
    fixed_current_time = datetime(2024, 8, 15, tzinfo=timezone.utc)
    mock_datetime.now.return_value = fixed_current_time
    mock_datetime.fromtimestamp = datetime.fromtimestamp
    mock_getmtime.side_effect = lambda path: datetime(2024, 6, 15, tzinfo=timezone.utc).timestamp()

    # Test
    dm.pipeline_cleaning(data_path, 2, "ont")

    # Assert
    stale_dirs = dm.find_stale_directories(data_path, 2)
    for item in stale_dirs:
        work_dir = os.path.join(item, "work")
        self.assertFalse(os.path.exists(work_dir))


@mock.patch("asf_tools.io.data_management.os.path.getmtime")
@mock.patch("asf_tools.io.data_management.datetime")
def test_pipeline_cleaning_doradofiles_valid(self, mock_datetime, mock_getmtime):
    """
    Test function with directories that have a mock editing time.
    Creates work dir, dorado dir structure, files within these folders and checks correct deletion of files.
    """
    # Set Up
    dm = DataManagement()

    # create work dir structure
    data_path = "tests/data/ont/runs"
    for root, dirs, files in os.walk(data_path):  # pylint: disable=unused-variable
        if root == data_path:
            for directory in dirs:
                work_dir = os.path.join(root, directory, "work")
                if not os.path.exists(work_dir):
                    os.makedirs(work_dir)
                file_workdir = os.path.join(work_dir, "dummy.txt")
                if not os.path.exists(file_workdir):
                    os.makedirs(file_workdir)

    # create dorado dir structure for multiple-sample run
    file_path1 = "tests/data/ont/runs/run01"
    dorado_dir1 = os.path.join(file_path1, "results", "dorado")
    dorado_demux_dir1 = os.path.join(dorado_dir1, "demux")
    file_dorado_dir1 = os.path.join(dorado_dir1, "dummy.txt")
    file_dorado_demux_dir1 = os.path.join(dorado_demux_dir1, "dummy.txt")
    if not os.path.exists(dorado_demux_dir1):
        os.makedirs(dorado_demux_dir1)
    if not os.path.exists(file_dorado_dir1):
        with open(file_dorado_dir1, "w"):
            pass
    if not os.path.exists(file_dorado_demux_dir1):
        with open(file_dorado_demux_dir1, "w"):
            pass
    # check files have been created correctly
    self.assertTrue(os.path.isfile(file_dorado_dir1))
    self.assertTrue(os.path.isfile(file_dorado_demux_dir1))

    # create dorado dir structure for 1-sample run
    file_path2 = "tests/data/ont/runs/run02"
    dorado_dir2 = os.path.join(file_path2, "results", "dorado")
    dorado_demux_dir2 = os.path.join(dorado_dir2, "demux")
    file_dorado_dir2 = os.path.join(dorado_dir2, "dummy.txt")
    file_dorado_demux_dir2 = os.path.join(dorado_demux_dir2, "dummy.txt")
    if not os.path.exists(dorado_demux_dir2):
        os.makedirs(dorado_demux_dir2)
    if not os.path.exists(file_dorado_dir2):
        with open(file_dorado_dir2, "w"):
            pass
    if not os.path.exists(file_dorado_demux_dir2):
        with open(file_dorado_demux_dir2, "w"):
            pass
    # check files have been created correctly
    self.assertTrue(os.path.isfile(file_dorado_dir2))
    self.assertTrue(os.path.isfile(file_dorado_demux_dir2))

    # set up mock structure
    fixed_current_time = datetime(2024, 8, 15, tzinfo=timezone.utc)
    mock_datetime.now.return_value = fixed_current_time
    mock_datetime.fromtimestamp = datetime.fromtimestamp
    mock_getmtime.side_effect = lambda path: datetime(2024, 6, 15, tzinfo=timezone.utc).timestamp()

    # Test
    dm.pipeline_cleaning(data_path, 2, "ont")

    # Assert
    self.assertTrue(os.path.isfile(file_dorado_dir1))
    self.assertTrue(os.path.isfile(file_dorado_demux_dir1))
    self.assertFalse(os.path.isfile(file_dorado_dir2))
    self.assertFalse(os.path.isfile(file_dorado_demux_dir2))
