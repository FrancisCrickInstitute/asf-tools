"""
Tests for ont gen demux run
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

import os
import stat

import pytest
from assertpy import assert_that

from asf_tools.api.clarity.clarity_helper_lims import ClarityHelperLims
from asf_tools.io.data_management import DataManagement, DataTypeMode
from asf_tools.io.storage_interface import InterfaceType, StorageInterface
from asf_tools.nextflow.gen_demux_run import check_runs_no_cli, create_ont_sbatch_text, extract_pipeline_params, run_cli
from asf_tools.nextflow.utils import create_sbatch_header
from tests.mocks.clarity_helper_lims_mock import ClarityHelperLimsMock


TEST_ONT_RUN_SOURCE_PATH = "tests/data/ont/runs"
TEST_ONT_LIVE_RUN_SOURCE_PATH = "tests/data/ont/live_runs"
TEST_ONT_PIPELINE_PATH = "tests/data/ont/nanopore_demux_pipeline"
API_TEST_DATA = "tests/data/api/clarity"


# Create class level mock API
@pytest.fixture(scope="class", autouse=True)
def mock_clarity_api(request):
    data_file_path = os.path.join(API_TEST_DATA, "mock_data", "helper-data.pkl")
    api = ClarityHelperLimsMock(baseuri="https://asf-claritylims.thecrick.org")
    api.load_tracked_requests(data_file_path)
    request.cls.api = api
    request.addfinalizer(lambda: api.save_tracked_requests(data_file_path))
    yield api


class TestGenDemuxRun:
    def test_ont_gen_demux_run_folder_creation_isvalid(self, tmp_path):
        # Setup
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_manager = DataManagement(storage_interface)

        # Test
        run_cli(
            api=self.api,
            storage_interface=storage_interface,
            data_manager=data_manager,
            data_type=DataTypeMode.ONT,
            source_dir=TEST_ONT_RUN_SOURCE_PATH,
            target_dir=tmp_path,
            run_name_contains=None,
            samplesheet_only=False,
            use_api=False,
            nextflow_version=None,
            nextflow_cache=".nextflow",
            nextflow_work="work",
            container_cache="sing",
            pipeline_dir=TEST_ONT_PIPELINE_PATH,
            runs_dir="runs",
        )

        # Assert
        run_dir_1 = os.path.join(tmp_path, "run01")
        run_dir_2 = os.path.join(tmp_path, "run02")
        run_dir_3 = os.path.join(tmp_path, "run03")
        run_dir_4 = os.path.join(tmp_path, "run04")

        assert_that(os.path.exists(run_dir_1)).is_true()
        assert_that(os.path.exists(run_dir_2)).is_true()
        assert_that(os.path.exists(run_dir_3)).is_false()
        assert_that(os.path.exists(run_dir_4)).is_true()

    def test_ont_gen_demux_run_folder_creation_with_contains(self, tmp_path):
        # Setup
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_manager = DataManagement(storage_interface)

        # Test
        run_cli(
            api=self.api,
            storage_interface=storage_interface,
            data_manager=data_manager,
            data_type=DataTypeMode.ONT,
            source_dir=TEST_ONT_RUN_SOURCE_PATH,
            target_dir=tmp_path,
            run_name_contains="run02",
            samplesheet_only=False,
            use_api=False,
            nextflow_version=None,
            nextflow_cache=".nextflow",
            nextflow_work="work",
            container_cache="sing",
            pipeline_dir=TEST_ONT_PIPELINE_PATH,
            runs_dir="runs",
        )

        # Assert
        run_dir_1 = os.path.join(tmp_path, "run01")
        run_dir_2 = os.path.join(tmp_path, "run02")

        assert_that(os.path.exists(run_dir_1)).is_false()
        assert_that(os.path.exists(run_dir_2)).is_true()

    def test_ont_gen_demux_run_sbatch_file_norm(self, tmp_path):
        # Setup
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_manager = DataManagement(storage_interface)

        # Test
        run_cli(
            api=self.api,
            storage_interface=storage_interface,
            data_manager=data_manager,
            data_type=DataTypeMode.ONT,
            source_dir=TEST_ONT_RUN_SOURCE_PATH,
            target_dir=tmp_path,
            run_name_contains=None,
            samplesheet_only=False,
            use_api=False,
            nextflow_version=None,
            nextflow_cache=".nextflow",
            nextflow_work="work",
            container_cache="sing",
            pipeline_dir=TEST_ONT_PIPELINE_PATH,
            runs_dir="runs",
        )

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
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_manager = DataManagement(storage_interface)

        # Test
        run_cli(
            api=self.api,
            storage_interface=storage_interface,
            data_manager=data_manager,
            data_type=DataTypeMode.ONT,
            source_dir=TEST_ONT_RUN_SOURCE_PATH,
            target_dir=tmp_path,
            run_name_contains=None,
            samplesheet_only=False,
            use_api=False,
            nextflow_version=None,
            nextflow_cache=".nextflow",
            nextflow_work="work",
            container_cache="sing",
            pipeline_dir=TEST_ONT_PIPELINE_PATH,
            runs_dir="runs",
        )

        # Assert
        samplesheet_path_01 = os.path.join(tmp_path, "run01", "samplesheet.csv")
        assert_that(os.path.exists(samplesheet_path_01)).is_true()

        with open(samplesheet_path_01, "r", encoding="UTF-8") as file:
            script_txt = "".join(file.readlines())

        assert_that(script_txt).contains("unclassified")

    def test_ont_gen_demux_run_file_permissions(self, tmp_path):
        # Setup
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_manager = DataManagement(storage_interface)

        # Test
        run_cli(
            api=self.api,
            storage_interface=storage_interface,
            data_manager=data_manager,
            data_type=DataTypeMode.ONT,
            source_dir=TEST_ONT_RUN_SOURCE_PATH,
            target_dir=tmp_path,
            run_name_contains=None,
            samplesheet_only=False,
            use_api=False,
            nextflow_version=None,
            nextflow_cache=".nextflow",
            nextflow_work="work",
            container_cache="sing",
            pipeline_dir=TEST_ONT_PIPELINE_PATH,
            runs_dir="runs",
        )

        # Assert
        run_file = os.path.join(tmp_path, "run01", "run_script.sh")
        file_status = os.stat(run_file)
        file_permissions = stat.S_IMODE(file_status.st_mode)
        executable = bool(file_permissions & os.X_OK)

        assert_that(executable).is_true()

    def test_ont_gen_demux_run_sbatch_file_nonfhome(self, tmp_path):
        # Setup
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_manager = DataManagement(storage_interface)

        # Test
        run_cli(
            api=self.api,
            storage_interface=storage_interface,
            data_manager=data_manager,
            data_type=DataTypeMode.ONT,
            source_dir=TEST_ONT_RUN_SOURCE_PATH,
            target_dir=tmp_path,
            run_name_contains=None,
            samplesheet_only=False,
            use_api=False,
            nextflow_version="20.10.0",
            nextflow_cache="",
            nextflow_work="work",
            container_cache="sing",
            pipeline_dir=TEST_ONT_PIPELINE_PATH,
            runs_dir="runs",
        )

        # Assert
        sbatch_path_01 = os.path.join(tmp_path, "run01", "run_script.sh")
        assert_that(os.path.exists(sbatch_path_01)).is_true()

        with open(sbatch_path_01, "r", encoding="UTF-8") as file:
            script_txt = "".join(file.readlines())

        assert_that(script_txt).does_not_contain("NXF_HOME")

    def test_ont_gen_demux_samplesheet_only(self, tmp_path):
        # Setup
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_manager = DataManagement(storage_interface)
        os.makedirs(os.path.join(tmp_path, "run01"))

        # Test
        run_cli(
            api=self.api,
            storage_interface=storage_interface,
            data_manager=data_manager,
            data_type=DataTypeMode.ONT,
            source_dir=TEST_ONT_RUN_SOURCE_PATH,
            target_dir=tmp_path,
            run_name_contains=None,
            samplesheet_only=True,
            use_api=False,
            nextflow_version=None,
            nextflow_cache=".nextflow",
            nextflow_work="work",
            container_cache="sing",
            pipeline_dir=TEST_ONT_PIPELINE_PATH,
            runs_dir="runs",
        )
        # Assert
        samplesheet_path_01 = os.path.join(tmp_path, "run01", "samplesheet.csv")
        assert_that(os.path.exists(samplesheet_path_01)).is_true()

    def test_ont_gen_demux_run_samplesheet_single_sample(self, tmp_path, monkeypatch):
        # Setup
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_manager = DataManagement(storage_interface)

        samplesheet_info_return = {
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
        monkeypatch.setattr(ClarityHelperLims, "collect_samplesheet_info", lambda uri, *args, **kwargs: samplesheet_info_return)

        # Test
        run_cli(
            api=self.api,
            storage_interface=storage_interface,
            data_manager=data_manager,
            data_type=DataTypeMode.ONT,
            source_dir=TEST_ONT_RUN_SOURCE_PATH,
            target_dir=tmp_path,
            run_name_contains=None,
            samplesheet_only=False,
            use_api=True,
            nextflow_version=None,
            nextflow_cache=".nextflow",
            nextflow_work="work",
            container_cache="sing",
            pipeline_dir=TEST_ONT_PIPELINE_PATH,
            runs_dir="runs",
        )

        # Setup Assertion
        samplesheet_path = os.path.join(tmp_path, "run01", "samplesheet.csv")
        with open(samplesheet_path, "r", encoding="UTF-8") as f:
            content = f.read()

        expected_content = (
            "id,sample_name,group,user,project_id,project_limsid,project_type,reference_genome,data_analysis_type,barcode\n"
            "sample_01,sample_01,asf,no_name,no_proj,no_lims_proj,no_type,no_ref,,unclassified\n"
        )

        # Assertion
        assert_that(content).is_equal_to(expected_content)

    def test_ont_gen_demux_run_samplesheet_multi_sample(self, tmp_path, monkeypatch):
        # Setup
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_manager = DataManagement(storage_interface)

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
        run_cli(
            api=self.api,
            storage_interface=storage_interface,
            data_manager=data_manager,
            data_type=DataTypeMode.ONT,
            source_dir=TEST_ONT_RUN_SOURCE_PATH,
            target_dir=tmp_path,
            run_name_contains=None,
            samplesheet_only=False,
            use_api=True,
            nextflow_version=None,
            nextflow_cache=".nextflow",
            nextflow_work="work",
            container_cache="sing",
            pipeline_dir=TEST_ONT_PIPELINE_PATH,
            runs_dir="runs",
        )

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

    def test_ont_gen_demux_run_extract_pipeline_params_isvalid(self, tmp_path):

        # Setup
        samplesheet_path = os.path.join(tmp_path, "samplesheet.csv")
        samplesheet_path_2 = os.path.join(tmp_path, "samplesheet2.csv")

        with open(samplesheet_path, "w", encoding="UTF-8") as file:
            file.write("id,project_id,project_limsid\n")
            file.write("sample_01,DN24086,no_lims_proj\n")

        with open(samplesheet_path_2, "w", encoding="UTF-8") as file:
            file.write("id,group,user,project_id\n")
            file.write("sample_01,asf,no_name,PM24043\n")

        expected_dict = {"Demux Pipeline Params": {"output_raw": "True"}}
        expected_dict_2 = {}

        # Test
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        results = extract_pipeline_params(self.api, storage_interface, samplesheet_path)
        results_2 = extract_pipeline_params(self.api, storage_interface, samplesheet_path_2)

        # Assert
        assert_that(results).is_equal_to(expected_dict)
        assert_that(results_2).is_equal_to(expected_dict_2)

    def test_ont_gen_demux_run_extract_pipeline_params_invalid_projectid(self, tmp_path):

        # Setup
        samplesheet_path = os.path.join(tmp_path, "samplesheet.csv")
        with open(samplesheet_path, "w", encoding="UTF-8") as file:
            file.write("id,sample_name,group,user,project_limsid,project_type,reference_genome,data_analysis_type,barcode\n")
            file.write("sample_01,sample_01,asf,no_name,no_lims_proj,no_type,no_ref,no_analysis,unclassified\n")

        # Test and Assert
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        assert_that(extract_pipeline_params(self.api, storage_interface, samplesheet_path)).is_equal_to({})

    def test_ont_gen_demux_check_runs_no_cli(self, tmp_path):
        # Setup
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_manager = DataManagement(storage_interface)

        # Test
        result = check_runs_no_cli(
            storage_interface=storage_interface, data_manager=data_manager, source_dir=TEST_ONT_RUN_SOURCE_PATH, target_dir=tmp_path, max_date=None
        )

        # Assert
        assert_that(result).is_equal_to(["run01", "run02", "run04", "run05"])

    # def test_ont_gen_demux_run_extract_pipeline_params_missing_projectid(self, tmp_path, caplog):

    #     # Setup
    #     samplesheet_path = os.path.join(tmp_path, "samplesheet.csv")
    #     with open(samplesheet_path, "w", encoding="UTF-8") as file:
    #         file.write("id,project_id,project_limsid\n")
    #         file.write("sample_01,no_proj,no_lims_proj\n")

    #     # Test and Assert
    #     GenDemuxRun.extract_pipeline_params(self, self.api, samplesheet_path)
    #     assert_that(caplog.text).contains("WARNING")

    def test_ont_gen_demux_run_create_sbatch_with_pipelineparams(self):
        # Setup
        run_name = "test_run"
        pipeline_params_dict = {"Demux Pipeline Params": {"output_raw": "True", "output_bam": "True"}}
        parse_pos = -1  # No parse position

        # Expected output without parse_pos
        expected_output = f"""#!/bin/sh

#SBATCH --partition=ncpu
#SBATCH --job-name=asf_nanopore_demux_{run_name}
#SBATCH --mem=4G
#SBATCH -n 1
#SBATCH --time=72:00:00
#SBATCH --output=run.o
#SBATCH --error=run.o
#SBATCH --res=asf

{create_sbatch_header("20.10.0")}

export NXF_HOME="/path/to/cache"
export NXF_WORK="/path/to/work"
export NXF_SINGULARITY_CACHEDIR="/path/to/container_cache"

nextflow run /path/to/pipeline \\
  -resume \\
  -profile crick,genomics \\
  --monochrome_logs \\
  --samplesheet ./samplesheet.csv \\
  --run_dir {os.path.join('/path/to/runs', run_name)} \\
  --dorado_model sup \\
  --output_raw True \\
  --output_bam True
"""
        result = create_ont_sbatch_text(
            run_name=run_name,
            pipeline_params_dict=pipeline_params_dict,
            nextflow_version="20.10.0",
            nextflow_cache="/path/to/cache",
            nextflow_work="/path/to/work",
            container_cache="/path/to/container_cache",
            pipeline_dir="/path/to/pipeline",
            run_file_runs_dir="/path/to/runs",
            parse_pos=parse_pos,
        )
        assert_that(result.strip()).is_equal_to(expected_output.strip())

    def test_ont_gen_demux_run_create_sbatch_without_parse_pos(self):
        # Setup
        run_name = "test_run"
        pipeline_params_dict = {}
        parse_pos = -1  # No parse position

        # Expected output without parse_pos
        expected_output = f"""#!/bin/sh

#SBATCH --partition=ncpu
#SBATCH --job-name=asf_nanopore_demux_{run_name}
#SBATCH --mem=4G
#SBATCH -n 1
#SBATCH --time=72:00:00
#SBATCH --output=run.o
#SBATCH --error=run.o
#SBATCH --res=asf

{create_sbatch_header("20.10.0")}

export NXF_HOME="/path/to/cache"
export NXF_WORK="/path/to/work"
export NXF_SINGULARITY_CACHEDIR="/path/to/container_cache"

nextflow run /path/to/pipeline \\
  -resume \\
  -profile crick,genomics \\
  --monochrome_logs \\
  --samplesheet ./samplesheet.csv \\
  --run_dir {os.path.join('/path/to/runs', run_name)} \\
  --dorado_model sup
"""
        result = create_ont_sbatch_text(
            run_name=run_name,
            pipeline_params_dict=pipeline_params_dict,
            nextflow_version="20.10.0",
            nextflow_cache="/path/to/cache",
            nextflow_work="/path/to/work",
            container_cache="/path/to/container_cache",
            pipeline_dir="/path/to/pipeline",
            run_file_runs_dir="/path/to/runs",
            parse_pos=parse_pos,
        )
        assert_that(result.strip()).is_equal_to(expected_output.strip())

    def test_ont_gen_demux_run_create_sbatch_with_parse_pos(self):
        # Create an instance of the class with required attributes
        run_name = "test_run"
        pipeline_params_dict = {}
        parse_pos = 2

        # Expected output with parse_pos
        expected_output = """#!/bin/sh

#SBATCH --partition=ncpu
#SBATCH --job-name=asf_nanopore_demux_test_run
#SBATCH --mem=4G
#SBATCH -n 1
#SBATCH --time=72:00:00
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
  -profile crick,genomics \\
  --monochrome_logs \\
  --samplesheet ./samplesheet.csv \\
  --run_dir /path/to/runs/test_run \\
  --dorado_model sup \\
  --dorado_bc_parse_pos 2

"""
        result = create_ont_sbatch_text(
            run_name=run_name,
            pipeline_params_dict=pipeline_params_dict,
            nextflow_version="20.10.0",
            nextflow_cache="/path/to/cache",
            nextflow_work="/path/to/work",
            container_cache="/path/to/container_cache",
            pipeline_dir="/path/to/pipeline",
            run_file_runs_dir="/path/to/runs",
            parse_pos=parse_pos,
        )
        assert_that(result.strip()).is_equal_to(expected_output.strip())

    def test_create_sbatch_with_pipelineparams_with_parse_pos(self):
        # Setup
        run_name = "test_run"
        pipeline_params_dict = {"Demux Pipeline Params": {"output_raw": "True", "output_bam": "True"}}
        parse_pos = 2  # No parse position

        # Expected output without parse_pos
        expected_output = f"""#!/bin/sh

#SBATCH --partition=ncpu
#SBATCH --job-name=asf_nanopore_demux_{run_name}
#SBATCH --mem=4G
#SBATCH -n 1
#SBATCH --time=72:00:00
#SBATCH --output=run.o
#SBATCH --error=run.o
#SBATCH --res=asf

{create_sbatch_header("20.10.0")}

export NXF_HOME="/path/to/cache"
export NXF_WORK="/path/to/work"
export NXF_SINGULARITY_CACHEDIR="/path/to/container_cache"

nextflow run /path/to/pipeline \\
  -resume \\
  -profile crick,genomics \\
  --monochrome_logs \\
  --samplesheet ./samplesheet.csv \\
  --run_dir {os.path.join('/path/to/runs', run_name)} \\
  --dorado_model sup \\
  --output_raw True \\
  --output_bam True \\
  --dorado_bc_parse_pos 2
"""
        result = create_ont_sbatch_text(
            run_name=run_name,
            pipeline_params_dict=pipeline_params_dict,
            nextflow_version="20.10.0",
            nextflow_cache="/path/to/cache",
            nextflow_work="/path/to/work",
            container_cache="/path/to/container_cache",
            pipeline_dir="/path/to/pipeline",
            run_file_runs_dir="/path/to/runs",
            parse_pos=parse_pos,
        )
        assert_that(result.strip()).is_equal_to(expected_output.strip())
