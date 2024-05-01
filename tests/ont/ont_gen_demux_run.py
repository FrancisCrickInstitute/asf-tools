"""
Tests for ont gen demux run
"""

import os

from asf_tools.ont.ont_gen_demux_run import OntGenDemuxRun
from ..utils import with_temporary_folder

TEST_ONT_RUN_SOURCE_PATH = "tests/data/ont/runs"


@with_temporary_folder
def test_folder_creation(self, tmp_path):
    """Test correct folder creation"""

    # Setup
    test = OntGenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, False)

    # Test
    test.run()

    # Assert
    run_dir_1 = os.path.join(tmp_path, "run01")
    run_dir_2 = os.path.join(tmp_path, "run02")
    run_dir_3 = os.path.join(tmp_path, "run03")

    self.assertTrue(os.path.exists(run_dir_1))
    self.assertTrue(os.path.exists(run_dir_2))
    self.assertFalse(os.path.exists(run_dir_3))


@with_temporary_folder
def test_sbatch_file(self, tmp_path):
    """Test correct folder creation"""

    # Setup
    test = OntGenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, False)

    # Test
    test.run()

    # Assert
    run_dir_1 = os.path.join(tmp_path, "run01")
    run_dir_2 = os.path.join(tmp_path, "run02")
    run_dir_3 = os.path.join(tmp_path, "run03")

    self.assertTrue(os.path.exists(run_dir_1))
    self.assertTrue(os.path.exists(run_dir_2))
    self.assertFalse(os.path.exists(run_dir_3))
