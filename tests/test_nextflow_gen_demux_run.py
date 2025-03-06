"""
Tests for ont gen demux run
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

import os
import stat
from assertpy import assert_that

from asf_tools.io.data_management import DataTypeMode
from asf_tools.nextflow.gen_demux_run import GenDemuxRun
from asf_tools.nextflow.utils import create_sbatch_header
from asf_tools.api.clarity.clarity_helper_lims import ClarityHelperLims

TEST_ONT_RUN_SOURCE_PATH = "tests/data/ont/runs"
TEST_ONT_LIVE_RUN_SOURCE_PATH = "tests/data/ont/live_runs"
TEST_ONT_PIPELINE_PATH = "tests/data/ont/nanopore_demux_pipeline"


class TestGenDemuxRun:
    def test_ont_gen_demux_run_folder_creation_isvalid(self, tmp_path):
        # Setup
        test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, ".nextflow", "sing", "work", "runs", False)

        # Test
        test.cli_run()

        # Assert
        run_dir_1 = os.path.join(tmp_path, "run01")
        run_dir_2 = os.path.join(tmp_path, "run02")
        run_dir_3 = os.path.join(tmp_path, "run03")
        run_dir_4 = os.path.join(tmp_path, "run04")

        assert_that(os.path.exists(run_dir_1)).is_true()
        assert_that(os.path.exists(run_dir_2)).is_true()
        assert_that(os.path.exists(run_dir_3)).is_false()
        assert_that(os.path.exists(run_dir_4)).is_false()

    def test_ont_gen_demux_run_folder_creation_with_contains(self, tmp_path):
        # Setup
        test = GenDemuxRun(
            TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, ".nextflow", "sing", "work", "runs", False, contains="run02"
        )

        # Test
        test.cli_run()

        # Assert
        run_dir_1 = os.path.join(tmp_path, "run01")
        run_dir_2 = os.path.join(tmp_path, "run02")

        assert_that(os.path.exists(run_dir_1)).is_false()
        assert_that(os.path.exists(run_dir_2)).is_true()

    def test_ont_gen_demux_run_sbatch_file_norm(self, tmp_path):
        # Setup
        test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, ".nextflow", "work", "sing", "runs", False)

        # Test
        test.cli_run()

        # Assert
        sbatch_path_01 = os.path.join(tmp_path, "run01", "run_script.sh")
        assert_that(os.path.exists(sbatch_path_01)).is_true()

        with open(sbatch_path_01, "r", encoding="UTF-8") as file:
            script_txt = "".join(file.readlines())

        assert_that(script_txt).contains("nextflow run")
        assert_that(script_txt).contains('export NXF_HOME=".nextflow"')
        assert_that(script_txt).contains('export NXF_WORK="work"')
        assert_that(script_txt).contains('export NXF_SINGULARITY_CACHEDIR="sing"')
        assert_that(script_txt).contains(f'--run_dir {os.path.join("runs", "run01")}')

    def test_ont_gen_demux_run_samplesheet_file_noapi(self, tmp_path):
        # Setup
        test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, ".nextflow", "sing", "work", "runs", False)

        # Test
        test.cli_run()

        # Assert
        samplesheet_path_01 = os.path.join(tmp_path, "run01", "samplesheet.csv")
        assert_that(os.path.exists(samplesheet_path_01)).is_true()

        with open(samplesheet_path_01, "r", encoding="UTF-8") as file:
            script_txt = "".join(file.readlines())

        assert_that(script_txt).contains("unclassified")

    def test_ont_gen_demux_run_file_permissions(self, tmp_path):
        # Setup
        test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, ".nextflow", "sing", "work", "runs", False)

        # Test
        test.cli_run()

        # Assert
        run_file = os.path.join(tmp_path, "run01", "run_script.sh")
        file_status = os.stat(run_file)
        file_permissions = stat.S_IMODE(file_status.st_mode)
        executable = bool(file_permissions & os.X_OK)

        assert_that(executable).is_true()

    def test_ont_gen_demux_run_sbatch_file_nonfhome(self, tmp_path):
        # Setup
        test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, "", "work", "sing", "runs", False)

        # Test
        test.cli_run()

        # Assert
        sbatch_path_01 = os.path.join(tmp_path, "run01", "run_script.sh")
        assert_that(os.path.exists(sbatch_path_01)).is_true()

        with open(sbatch_path_01, "r", encoding="UTF-8") as file:
            script_txt = "".join(file.readlines())

        assert_that(script_txt).does_not_contain("NXF_HOME")

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
        test.cli_run()

        # Assert
        samplesheet_path_01 = os.path.join(tmp_path, "run01", "samplesheet.csv")
        assert_that(os.path.exists(samplesheet_path_01)).is_true()

    # @patch("asf_tools.api.clarity.clarity_helper_lims.ClarityHelperLims.collect_samplesheet_info")
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
                "barcode": None,  # Unclassified
            }
        }

        # Test
        test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, "", "work", "sing", "runs", True)
        test.cli_run()

        # Setup Assertion
        samplesheet_path = os.path.join(tmp_path, "run01", "samplesheet.csv")
        with open(samplesheet_path, "r", encoding="UTF-8") as f:
            content = f.read()

        expected_content = (
            "id,sample_name,group,user,project_id,project_limsid,project_type,reference_genome,data_analysis_type,barcode\n"
            "sample_01,sample_01,asf,no_name,no_proj,no_lims_proj,no_type,no_ref,,unclassified\n"
        )

        # Assertion
        self.assertEqual(content, expected_content)

    def test_ont_gen_demux_samplesheet_multi_sample(self, tmp_path, monkeypatch):
        # Setup
        samplesheet_info_return = {
            "sample_01": {
                "sample_name": "sample_01",
                "group": "asf",
                "user": "no_name",
                "project_id": "no_proj",
                "project_limsid": "no_lims_proj",
                "project_type": "no_type",
                "reference_genome": None,
                "data_analysis_type": "no_analysis",
                "barcode": "barcode01",  # Barcoded
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
                "barcode": "barcode02",  # Barcoded
            },
        }
        monkeypatch.setattr(ClarityHelperLims, "collect_samplesheet_info", lambda uri, *args, **kwargs: samplesheet_info_return)

        # Test
        test = GenDemuxRun(TEST_ONT_RUN_SOURCE_PATH, tmp_path, DataTypeMode.ONT, TEST_ONT_PIPELINE_PATH, "", "work", "sing", "runs", True)
        test.cli_run()

        # Setup Assertion
        samplesheet_path = os.path.join(tmp_path, "run01", "samplesheet.csv")
        with open(samplesheet_path, "r", encoding="UTF-8") as f:
            content = f.read()
        expected_content = (
            "id,sample_name,group,user,project_id,project_limsid,project_type,reference_genome,data_analysis_type,barcode\n"
            "sample_01,sample_01,asf,no_name,no_proj,no_lims_proj,no_type,,no_analysis,barcode01\n"
            "sample_02,sample_02,asf,no_name,no_proj,no_lims_proj,no_type,,no_analysis,barcode02\n"
        )

        # Assertion
        assert_that(content).is_equal_to(expected_content)

    def test_create_sbatch_without_parse_pos(self):
        # Create an instance of the class with required attributes
        instance = GenDemuxRun(
            source_dir="/path/to/source",
            target_dir="/path/to/target",
            mode="ONT",
            pipeline_dir="/path/to/pipeline",
            nextflow_cache="/path/to/cache",
            nextflow_work="/path/to/work",
            container_cache="/path/to/container_cache",
            runs_dir="/path/to/runs",
            use_api=False,
            nextflow_version="20.10.0",
        )

        run_name = "test_run"
        parse_pos = -1  # No parse position

        # Expected output without parse_pos
        expected_output = f"""#!/bin/sh

#SBATCH --partition=ncpu
#SBATCH --job-name=asf_nanopore_demux_{run_name}
#SBATCH --mem=4G
#SBATCH -n 1
#SBATCH --time=168:00:00
#SBATCH --output=run.o
#SBATCH --error=run.o
#SBATCH --res=asf

{create_sbatch_header("20.10.0")}

export NXF_HOME="/path/to/cache"
export NXF_WORK="/path/to/work"
export NXF_SINGULARITY_CACHEDIR="/path/to/container_cache"

nextflow run /path/to/pipeline \\
  -resume \\
  -profile crick,nemo \\
  --monochrome_logs \\
  --samplesheet ./samplesheet.csv \\
  --run_dir {os.path.join('/path/to/runs', run_name)} \\
  --dorado_model sup
"""
        result = instance.create_ont_sbatch_text(run_name, parse_pos)
        assert_that(result.strip()).is_equal_to(expected_output.strip())


    def test_create_sbatch_with_parse_pos(self):
        # Create an instance of the class with required attributes
        instance = GenDemuxRun(
            source_dir="/path/to/source",
            target_dir="/path/to/target",
            mode="ONT",
            pipeline_dir="/path/to/pipeline",
            nextflow_cache="/path/to/cache",
            nextflow_work="/path/to/work",
            container_cache="/path/to/container_cache",
            runs_dir="/path/to/runs",
            use_api=False,
            nextflow_version="20.10.0",
        )
        run_name = "test_run"
        parse_pos = 2

        # Expected output with parse_pos
        expected_output = """#!/bin/sh

#SBATCH --partition=ncpu
#SBATCH --job-name=asf_nanopore_demux_test_run
#SBATCH --mem=4G
#SBATCH -n 1
#SBATCH --time=168:00:00
#SBATCH --output=run.o
#SBATCH --error=run.o
#SBATCH --res=asf

ml purge
ml Nextflow/20.10.0
ml Singularity/3.6.4


export NXF_HOME="/path/to/cache"
export NXF_WORK="/path/to/work"
export NXF_SINGULARITY_CACHEDIR="/path/to/container_cache"

nextflow run /path/to/pipeline \\
  -resume \\
  -profile crick,nemo \\
  --monochrome_logs \\
  --samplesheet ./samplesheet.csv \\
  --run_dir /path/to/runs/test_run \\
  --dorado_model sup \\
  --dorado_bc_parse_pos 2

"""

        result = instance.create_ont_sbatch_text(run_name, parse_pos)
        print(result)
        assert_that(result.strip()).is_equal_to(expected_output.strip())
