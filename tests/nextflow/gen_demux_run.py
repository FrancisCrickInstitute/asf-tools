"""
Tests for ont gen demux run
"""
# pylint: disable=missing-function-docstring

import os
import stat
from unittest.mock import patch

from asf_tools.io.data_management import DataTypeMode
from asf_tools.nextflow.gen_demux_run import GenDemuxRun

from ..utils import with_temporary_folder


TEST_ONT_RUN_SOURCE_PATH = "tests/data/ont/runs"
TEST_ONT_LIVE_RUN_SOURCE_PATH = "tests/data/ont/live_runs"
TEST_ONT_PIPELINE_PATH = "tests/data/ont/nanopore_demux_pipeline"


@with_temporary_folder
def test_ont_gen_demux_run_folder_creation_isvalid(self, tmp_path):
    # Setup
    test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, ".nextflow", "sing", "work", "runs", False)

    # Test
    test.run()

    # Assert
    run_dir_1 = os.path.join(tmp_path, "run01")
    run_dir_2 = os.path.join(tmp_path, "run02")
    run_dir_3 = os.path.join(tmp_path, "run03")
    run_dir_4 = os.path.join(tmp_path, "run04")

    self.assertTrue(os.path.exists(run_dir_1))
    self.assertTrue(os.path.exists(run_dir_2))
    self.assertFalse(os.path.exists(run_dir_3))
    self.assertFalse(os.path.exists(run_dir_4))


@with_temporary_folder
def test_ont_gen_demux_run_folder_creation_with_contains(self, tmp_path):
    # Setup
    test = GenDemuxRun(
        TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, ".nextflow", "sing", "work", "runs", False, contains="run02"
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
    # Setup
    test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, ".nextflow", "work", "sing", "runs", False)

    # Test
    test.run()

    # Assert
    sbatch_path_01 = os.path.join(tmp_path, "run01", "run_script.sh")

    self.assertTrue(os.path.exists(sbatch_path_01))

    with open(sbatch_path_01, "r", encoding="UTF-8") as file:
        script_txt = "".join(file.readlines())

    print(script_txt)
    self.assertTrue("nextflow run" in script_txt)
    self.assertTrue('export NXF_HOME=".nextflow"' in script_txt)
    self.assertTrue('export NXF_WORK="work"' in script_txt)
    self.assertTrue('export NXF_SINGULARITY_CACHEDIR="sing"' in script_txt)
    self.assertTrue(f'--run_dir {os.path.join("runs", "run01")}' in script_txt)


@with_temporary_folder
def test_ont_gen_demux_run_samplesheet_file_noapi(self, tmp_path):
    # Setup
    test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, ".nextflow", "sing", "work", "runs", False)

    # Test
    test.run()

    # Assert
    samplesheet_path_01 = os.path.join(tmp_path, "run01", "samplesheet.csv")

    self.assertTrue(os.path.exists(samplesheet_path_01))

    with open(samplesheet_path_01, "r", encoding="UTF-8") as file:
        script_txt = "".join(file.readlines())

    print(script_txt)
    self.assertTrue("unclassified" in script_txt)


@with_temporary_folder
def test_ont_gen_demux_run_file_permissions(self, tmp_path):
    # Setup
    test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, ".nextflow", "sing", "work", "runs", False)

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
    # Setup
    test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, "", "work", "sing", "runs", False)

    # Test
    test.run()

    # Assert
    sbatch_path_01 = os.path.join(tmp_path, "run01", "run_script.sh")

    self.assertTrue(os.path.exists(sbatch_path_01))

    with open(sbatch_path_01, "r", encoding="UTF-8") as file:
        script_txt = "".join(file.readlines())

    print(script_txt)
    self.assertFalse("NXF_HOME" in script_txt)


@with_temporary_folder
def test_ont_gen_demux_samplesheet_only(self, tmp_path):
    # Setup
    test = GenDemuxRun(
        TEST_ONT_RUN_SOURCE_PATH,
        tmp_path,
        DataTypeMode.ONT,
        TEST_ONT_PIPELINE_PATH,
        ".nextflow",
        "sing",
        "work",
        "runs",
        False,
        samplesheet_only=True,
    )

    os.makedirs(os.path.join(tmp_path, "run01"))

    # Test
    test.run()

    # Assert
    samplesheet_path_01 = os.path.join(tmp_path, "run01", "samplesheet.csv")

    self.assertTrue(os.path.exists(samplesheet_path_01))


@patch('asf_tools.api.clarity.clarity_helper_lims.ClarityHelperLims.collect_samplesheet_info')
@with_temporary_folder
def test_ont_gen_demux_samplesheet_single_sample(self, mock_collect_samplesheet_info, tmp_path):
    # Setup
    mock_collect_samplesheet_info.return_value = {
        "sample_01": {
            "sample_name": "sample_01",
            "group": "asf",
            "user": "no_name",
            "project_id": "no_proj",
            "project_limsid": "no_lims_proj",
            "project_type": "no_type",
            "reference_genome": "no_ref",
            "data_analysis_type": None,
            "barcode": None  # Unclassified
        }
    }

    # Test
    test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, "", "work", "sing", "runs", True)
    test.run()

    # Setup Assertion
    samplesheet_path = os.path.join(tmp_path, 'run01', 'samplesheet.csv')
    with open(samplesheet_path, 'r', encoding="UTF-8") as f:
        content = f.read()

    expected_content = (
        "id,sample_name,group,user,project_id,project_limsid,project_type,reference_genome,data_analysis_type,barcode\n"
        "sample_01,sample_01,asf,no_name,no_proj,no_lims_proj,no_type,no_ref,,unclassified\n"
    )

    # Assertion
    self.assertEqual(content, expected_content)


@patch('asf_tools.api.clarity.clarity_helper_lims.ClarityHelperLims.collect_samplesheet_info')
@with_temporary_folder
def test_ont_gen_demux_samplesheet_multi_sample(self, mock_collect_samplesheet_info, tmp_path):
    # Setup
    mock_collect_samplesheet_info.return_value = {
        "sample_01": {
            "sample_name": "sample_01",
            "group": "asf",
            "user": "no_name",
            "project_id": "no_proj",
            "project_limsid": "no_lims_proj",
            "project_type": "no_type",
            "reference_genome": None,
            "data_analysis_type": "no_analysis",
            "barcode": "barcode01"  # Barcoded
        },
        "sample_02": {
            "sample_name": "sample_02",
            "group": "asf",
            "user": "no_name",
            "project_id": "no_proj",
            "project_limsid": "no_lims_proj",
            "project_type": "no_type",
            "reference_genome": None,
            "data_analysis_type": "no_analysis",
            "barcode": "barcode02"  # Barcoded
        }
    }

    # Test
    test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, "", "work", "sing", "runs", True)
    test.run()

    # Setup Assertion
    samplesheet_path = os.path.join(tmp_path, 'run01', 'samplesheet.csv')
    with open(samplesheet_path, 'r', encoding="UTF-8") as f:
        content = f.read()

    expected_content = (
        "id,sample_name,group,user,project_id,project_limsid,project_type,reference_genome,data_analysis_type,barcode\n"
        "sample_01,sample_01,asf,no_name,no_proj,no_lims_proj,no_type,,no_analysis,barcode01\n"
        "sample_02,sample_02,asf,no_name,no_proj,no_lims_proj,no_type,,no_analysis,barcode02\n"
    )

    # Assertion
    self.assertEqual(content, expected_content)
