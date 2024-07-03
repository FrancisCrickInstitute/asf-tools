"""
Tests for ont gen demux run
"""

import os
import stat

from asf_tools.ont.ont_gen_demux_run import OntGenDemuxRun

from ..utils import with_temporary_folder


TEST_ONT_RUN_SOURCE_PATH = "tests/data/ont/runs"
TEST_ONT_PIPELINE_PATH = "tests/data/ont/nanopore_demux_pipeline"


@with_temporary_folder
def test_ont_gen_demux_run_folder_creation(self, tmp_path):
    """ONT Gen demux run tests"""

    # Setup
    test = OntGenDemuxRun(
        TEST_ONT_RUN_SOURCE_PATH,
        tmp_path,
        TEST_ONT_PIPELINE_PATH,
        ".nextflow",
        "sing",
        "work",
        "runs",
        False,
        False,
    )

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
def test_ont_gen_demux_run_folder_creation_with_contains(self, tmp_path):
    """ONT Gen demux run tests"""

    # Setup
    test = OntGenDemuxRun(
        TEST_ONT_RUN_SOURCE_PATH,
        tmp_path,
        TEST_ONT_PIPELINE_PATH,
        ".nextflow",
        "sing",
        "work",
        "runs",
        False,
        False,
        "run02",
    )

    # Test
    test.run()

    # Assert
    run_dir_1 = os.path.join(tmp_path, "run01")
    run_dir_2 = os.path.join(tmp_path, "run02")

    self.assertFalse(os.path.exists(run_dir_1))
    self.assertTrue(os.path.exists(run_dir_2))


@with_temporary_folder
def test_ont_gen_demux_run_sbatch_file(self, tmp_path):
    """ONT Gen demux run tests"""

    # Setup
    test = OntGenDemuxRun(
        TEST_ONT_RUN_SOURCE_PATH,
        tmp_path,
        TEST_ONT_PIPELINE_PATH,
        ".nextflow",
        "work",
        "sing",
        "runs",
        False,
        False,
    )

    # Test
    test.run()

    # Assert
    sbatch_path_01 = os.path.join(tmp_path, "run01", "run_script.sh")
    sbatch_path_02 = os.path.join(tmp_path, "run02", "run_script.sh")

    self.assertTrue(os.path.exists(sbatch_path_01))
    self.assertTrue(os.path.exists(sbatch_path_02))

    with open(sbatch_path_01, "r", encoding="UTF-8") as file:
        script_txt = "".join(file.readlines())

    print(script_txt)
    self.assertTrue("nextflow run" in script_txt)
    self.assertTrue('export NXF_HOME=".nextflow"' in script_txt)
    self.assertTrue('export NXF_WORK="work"' in script_txt)
    self.assertTrue('export NXF_SINGULARITY_CACHEDIR="sing"' in script_txt)
    self.assertTrue(f'--run_dir {os.path.join("runs", "run01")}' in script_txt)


@with_temporary_folder
def test_ont_gen_demux_run_samplesheet_file(self, tmp_path):
    """ONT Gen demux run tests"""

    # Setup
    test = OntGenDemuxRun(
        TEST_ONT_RUN_SOURCE_PATH,
        tmp_path,
        TEST_ONT_PIPELINE_PATH,
        ".nextflow",
        "sing",
        "work",
        "runs",
        False,
        False,
    )

    # Test
    test.run()

    # Assert
    samplesheet_path_01 = os.path.join(tmp_path, "run01", "samplesheet.csv")
    samplesheet_path_02 = os.path.join(tmp_path, "run02", "samplesheet.csv")

    self.assertTrue(os.path.exists(samplesheet_path_01))
    self.assertTrue(os.path.exists(samplesheet_path_02))

    with open(samplesheet_path_01, "r", encoding="UTF-8") as file:
        script_txt = "".join(file.readlines())

    print(script_txt)
    self.assertTrue("unclassified" in script_txt)


@with_temporary_folder
def test_ont_gen_demux_run_file_permissions(self, tmp_path):
    """ONT Gen demux run tests"""

    # Setup
    test = OntGenDemuxRun(
        TEST_ONT_RUN_SOURCE_PATH,
        tmp_path,
        TEST_ONT_PIPELINE_PATH,
        ".nextflow",
        "sing",
        "work",
        "runs",
        False,
        False,
    )

    # Test
    test.run()

    # Assert
    run_file = os.path.join(tmp_path, "run01", "run_script.sh")
    file_status = os.stat(run_file)
    file_permissions = stat.S_IMODE(file_status.st_mode)
    executable = bool(file_permissions & os.X_OK)

    self.assertTrue(executable)


@with_temporary_folder
def test_ont_gen_demux_run_sbatch_file_nonfhome(self, tmp_path):
    """ONT Gen demux run tests"""

    # Setup
    test = OntGenDemuxRun(
        TEST_ONT_RUN_SOURCE_PATH,
        tmp_path,
        TEST_ONT_PIPELINE_PATH,
        "",
        "work",
        "sing",
        "runs",
        False,
        False,
    )

    # Test
    test.run()

    # Assert
    sbatch_path_01 = os.path.join(tmp_path, "run01", "run_script.sh")
    sbatch_path_02 = os.path.join(tmp_path, "run02", "run_script.sh")

    self.assertTrue(os.path.exists(sbatch_path_01))
    self.assertTrue(os.path.exists(sbatch_path_02))

    with open(sbatch_path_01, "r", encoding="UTF-8") as file:
        script_txt = "".join(file.readlines())

    print(script_txt)
    self.assertFalse("NXF_HOME" in script_txt)
