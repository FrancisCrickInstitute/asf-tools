"""
Tests for ont gen demux run
"""

import os

from asf_tools.ont.ont_gen_demux_run import OntGenDemuxRun
from ..utils import with_temporary_folder

TEST_ONT_RUN_SOURCE_PATH = "tests/data/ont/runs"
TEST_ONT_PIPELINE_PATH = "tests/data/ont/nanopore_demux_pipeline"


@with_temporary_folder
def test_folder_creation(self, tmp_path):
    """Test correct folder creation"""

    # Setup
    test = OntGenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, TEST_ONT_PIPELINE_PATH, False)

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
    """Test correct sbatch file creation"""

    # Setup
    test = OntGenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, TEST_ONT_PIPELINE_PATH, False)

    # Test
    test.run()

    # Assert
    sbatch_path_01 = os.path.join(tmp_path, "run01", "run_script.sh")
    sbatch_path_02 = os.path.join(tmp_path, "run02", "run_script.sh")

    self.assertTrue(os.path.exists(sbatch_path_01))
    self.assertTrue(os.path.exists(sbatch_path_02))

    with open(sbatch_path_01, "r", encoding="UTF-8") as file:
        script_txt = "".join(file.readlines())

    self.assertTrue("nextflow run" in script_txt)


@with_temporary_folder
def test_samplesheet_file(self, tmp_path):
    """Test correct samplesheet creation"""

    # Setup
    test = OntGenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, TEST_ONT_PIPELINE_PATH, False)

    # Test
    test.run()

    # Assert
    samplesheet_path_01 = os.path.join(tmp_path, "run01", "samplesheet.csv")
    samplesheet_path_02 = os.path.join(tmp_path, "run02", "samplesheet.csv")

    self.assertTrue(os.path.exists(samplesheet_path_01))
    self.assertTrue(os.path.exists(samplesheet_path_02))

    with open(samplesheet_path_01, "r", encoding="UTF-8") as file:
        script_txt = "".join(file.readlines())

    self.assertTrue("unclassified" in script_txt)
