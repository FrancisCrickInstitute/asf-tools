"""
Illumina data wrangling tests
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member


import json
import os
from unittest import mock

import pytest
from assertpy import assert_that

from asf_tools.illumina.illumina_data_wrangling import generate_illumina_demux_samplesheets
from asf_tools.illumina.illumina_utils import count_samples_in_bcl_samplesheet
from tests.mocks.clarity_helper_lims_mock import ClarityHelperLimsMock


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


class TestIlluminaDemux:
    """Class for testing the generate_illumina_samplesheet tools"""

    def test_generate_illumina_demux_samplesheets_bulk(self, tmp_path):
        """
        Pass real run ID with bulk/non-singlecell samples, check that a samplesheet is generated and its content
        """

        # Set up
        file = "./tests/data/illumina/22NWWGLT3/RunInfo.xml"
        # create output files paths
        tmp_bclconfig_file_path = os.path.join(tmp_path, "bcl_config_22NWWGLT3.json")
        tmp_samplesheet_file_path_bulk = os.path.join(tmp_path, "22NWWGLT3_samplesheet_8_8.csv")
        tmp_samplesheet_file_path_general = os.path.join(tmp_path, "22NWWGLT3_samplesheet.csv")

        # Test
        generate_illumina_demux_samplesheets(self.api, file, tmp_path)

        # Assert
        assert_that(os.path.exists(tmp_samplesheet_file_path_bulk)).is_true()
        assert_that(os.path.exists(tmp_bclconfig_file_path)).is_true()

        # Check the content of the files
        with open(tmp_samplesheet_file_path_general, "r") as file:
            data = "".join(file.readlines())
            assert_that(data).contains("[BCLConvert_Data]")
            assert_that(data).contains("Lane,Sample_ID,index,index2")
        with open(tmp_samplesheet_file_path_bulk, "r") as file:
            data = "".join(file.readlines())
            assert_that(data).contains("[BCLConvert_Data]")
            assert_that(data).contains("Lane,Sample_ID,index,index2")
            assert_that(data).contains("WAR6617A6,TCTTCTCG,TATCTCAT")
        with open(tmp_bclconfig_file_path, "r") as file:
            config_json = json.load(file)
            assert_that(config_json).contains("Header")

        # Check the number of samples for each samplesheet
        samples_general = count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path_general, "Sample_ID")
        samples_bulk = count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path_bulk, "Sample_ID")

        expected_unique_samples_entries_general = 32
        expected_unique_samples_entries_bulk = 32

        assert_that(samples_general).is_equal_to(expected_unique_samples_entries_general)
        assert_that(samples_bulk).is_equal_to(expected_unique_samples_entries_bulk)

    def test_generate_illumina_demux_samplesheets_singlecell(self, tmp_path):
        """
        Pass real run ID with singlecell samples, check that a samplesheet is generated and its content
        """

        # Set up
        file = "./tests/data/illumina/22T3M3LT3/RunInfo.xml"
        # create output files paths
        tmp_bclconfig_file_path = os.path.join(tmp_path, "bcl_config_22T3M3LT3.json")
        tmp_samplesheet_file_path = os.path.join(tmp_path, "22T3M3LT3_samplesheet_singlecell.csv")

        # Test
        generate_illumina_demux_samplesheets(self.api, file, tmp_path)

        # Assert
        assert_that(os.path.exists(tmp_samplesheet_file_path)).is_true()
        assert_that(os.path.exists(tmp_bclconfig_file_path)).is_true()

        # Check the content of the files
        with open(tmp_bclconfig_file_path, "r") as file:
            config_json = json.load(file)
            assert_that(config_json).contains("Header")
        with open(tmp_samplesheet_file_path, "r") as file:
            data = "".join(file.readlines())
            assert_that(data).contains("[BCLConvert_Data]")
            assert_that(data).contains("Lane,Sample_ID,index,index2")

        # Check the number of samples
        samples_singlecell = count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path, "Sample_ID")
        expected_unique_samples_entries_singlecell = 136
        assert_that(samples_singlecell).is_equal_to(expected_unique_samples_entries_singlecell)

    def test_generate_illumina_demux_samplesheets_dlp(self, tmp_path):
        """
        Pass real run ID with singlecell samples, check that a samplesheet is generated and its content
        """

        # Set up
        runinfo_file = "./tests/data/illumina/HWNCWDMXY/RunInfo.xml"
        dlp_file = "./tests/data/illumina/dlp_barcode_extended_info_testdataset.csv"

        # create output files paths
        tmp_samplesheet_file_path = os.path.join(tmp_path, "HWNCWDMXY_samplesheet_dlp.csv")
        tmp_bclconfig_file_path = os.path.join(tmp_path, "bcl_config_HWNCWDMXY.json")

        # Test
        generate_illumina_demux_samplesheets(self.api, runinfo_file, tmp_path, dlp_sample_file=dlp_file)

        # Assert
        assert_that(os.path.exists(tmp_samplesheet_file_path)).is_true()
        assert_that(os.path.exists(tmp_bclconfig_file_path)).is_true()

        # Check the content of the files
        with open(tmp_bclconfig_file_path, "r") as file:
            config_json = json.load(file)
            assert_that(config_json).contains("Header")
        with open(tmp_samplesheet_file_path, "r") as file:
            data = "".join(file.readlines())
            assert_that(data).contains("[BCLConvert_Data]")
            assert_that(data).contains("Lane,Sample_ID,index,index2")
            assert_that(data).contains("CAACCTAG,AGGTCTGT")

        # Check the number of samples
        samples_dlp = count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path, "Sample_ID")
        expected_unique_samples_entries_dlp = 12
        assert_that(samples_dlp).is_equal_to(expected_unique_samples_entries_dlp)

    def test_generate_illumina_demux_samplesheets_mix(self, tmp_path):
        """
        Pass real run ID with singlecell samples, check that a samplesheet is generated and its content
        """

        # Set up
        run_info_path = "./tests/data/illumina/22NWWGLT3/RunInfo.xml"
        mock_sample_info = "./tests/data/api/clarity/mock_data/22NWWGLT3_sample_info_mock.json"

        # Create output file paths
        tmp_bclconfig_file_path = os.path.join(tmp_path, "bcl_config_22NWWGLT3.json")
        tmp_samplesheet_file_path_bulk = os.path.join(tmp_path, "22NWWGLT3_samplesheet_8_8.csv")
        tmp_samplesheet_file_path_atac = os.path.join(tmp_path, "22NWWGLT3_samplesheet_atac.csv")
        tmp_samplesheet_file_path_sc = os.path.join(tmp_path, "22NWWGLT3_samplesheet_singlecell.csv")
        tmp_samplesheet_file_path_general = os.path.join(tmp_path, "22NWWGLT3_samplesheet.csv")

        # Extract mocked sample info from the json file
        # Load the content of the JSON file into the 'info' variable
        with open(mock_sample_info, "r") as json_file:
            json_info = json.load(json_file)
        with mock.patch("asf_tools.api.clarity.clarity_helper_lims.ClarityHelperLims") as mock_lims:
            # Create a mock instance of ClarityHelperLims
            mock_cl = mock_lims.return_value
            mock_cl.collect_samplesheet_info.return_value = json_info

            # Test
            generate_illumina_demux_samplesheets(mock_cl, run_info_path, tmp_path)

            # Assert
            assert_that(os.path.exists(tmp_bclconfig_file_path)).is_true()
            assert_that(os.path.exists(tmp_samplesheet_file_path_bulk)).is_true()
            assert_that(os.path.exists(tmp_samplesheet_file_path_atac)).is_true()
            assert_that(os.path.exists(tmp_samplesheet_file_path_sc)).is_true()
            assert_that(os.path.exists(tmp_samplesheet_file_path_general)).is_true()

            # Check the content of the files
            with open(tmp_bclconfig_file_path, "r") as file:
                config_json = json.load(file)
                assert_that(config_json).contains("Header")
            with open(tmp_samplesheet_file_path_bulk, "r") as file:
                data = "".join(file.readlines())
                assert_that(data).contains("[BCLConvert_Data]")
                assert_that(data).contains("Lane,Sample_ID,index,index2")
            with open(tmp_samplesheet_file_path_general, "r") as file:
                data = "".join(file.readlines())
                assert_that(data).contains("[BCLConvert_Data]")
                assert_that(data).contains("Lane,Sample_ID,index,index2")
            # Check the content of the files
            with open(tmp_samplesheet_file_path_atac, "r") as file:
                data = "".join(file.readlines())
                assert_that(data).contains("Lane,Sample_ID,index,index2")
                assert_that(data).contains("WAR6617A6,GGAAGAGA")
                assert_that(data).contains("WAR6617A6,CGAGAGAA")
            with open(tmp_samplesheet_file_path_bulk, "r") as file:
                data = "".join(file.readlines())
                assert_that(data).contains("Lane,Sample_ID,index,index2")
                assert_that(data).contains("WAR6617A1,CGAATTGC,GTAAGGTG")
            with open(tmp_samplesheet_file_path_sc, "r") as file:
                data = "".join(file.readlines())
                assert_that(data).contains("Lane,Sample_ID,index,index2")
                assert_that(data).contains("WAR6617A2,GGAAGAGA,CGAGAGAA")

            # Check the number of samples for each samplesheet
            samples_general = count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path_general, "Sample_ID")
            samples_bulk = count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path_bulk, "Sample_ID")
            samples_sc = count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path_sc, "Sample_ID")
            samples_atac = count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path_atac, "Sample_ID")

            expected_unique_samples_entries_bulk = 27  # 7 samples
            expected_unique_samples_entries_sc = 33  # 8 samples
            expected_unique_samples_entries_atac = 190  # 9 samples
            expected_unique_samples_entries_general = 108

            assert_that(samples_general).is_equal_to(expected_unique_samples_entries_general)
            assert_that(samples_bulk).is_equal_to(expected_unique_samples_entries_bulk)
            assert_that(samples_sc).is_equal_to(expected_unique_samples_entries_sc)
            assert_that(samples_atac).is_equal_to(expected_unique_samples_entries_atac)

    @pytest.mark.parametrize(
        "flowcell_id,runinfo_file,samplesheet_count",
        [
            ("22NWYFLT3", "./tests/data/illumina/22NWYFLT3/RunInfo.xml", 4),
            ("22NWWMLT3", "./tests/data/illumina/22NWWMLT3/RunInfo.xml", 5),
            ("22G57KLT4", "./tests/data/illumina/22G57KLT4/RunInfo.xml", 2),  # 1 general samplesheet, 1 project specific samplesheet
        ],
    )
    def test_generate_illumina_demux_samplesheets_withfixtures(self, flowcell_id, runinfo_file, samplesheet_count, tmp_path):
        """
        Pass real runs with a mix of samples with different project types and/or index length.
        Check that a samplesheet are generated, how many and their content
        """
        # Set up
        # create output files paths
        bclconfig_name = "bcl_config_" + flowcell_id + ".json"
        tmp_bclconfig_file_path = os.path.join(tmp_path, bclconfig_name)

        # Test
        generate_illumina_demux_samplesheets(self.api, runinfo_file, tmp_path)

        # Assert
        assert os.path.exists(tmp_bclconfig_file_path)

        # Check the content of the files
        with open(tmp_bclconfig_file_path, "r") as file:
            config_json = json.load(file)
            assert "Header" in config_json

        # Verify the number of SampleSheet files
        samplesheet_files = [f for f in os.listdir(tmp_path) if "samplesheet" in f.lower() and os.path.isfile(os.path.join(tmp_path, f))]
        print(samplesheet_files)
        assert len(samplesheet_files) == samplesheet_count

        general_samplesheet_name = os.path.join(tmp_path, flowcell_id + "_samplesheet.csv")
        # print(general_samplesheet_name)
        # Check the content of the files
        with open(general_samplesheet_name, "r") as file:
            data = "".join(file.readlines())
            assert "[BCLConvert_Data]" in data
            assert "Lane,Sample_ID" in data
            assert "Lane,Sample_ID,index,index2" in data

        for samplesheet in samplesheet_files:
            samplesheet_name = os.path.join(tmp_path, samplesheet)
            with open(samplesheet_name, "r") as file:
                data = "".join(file.readlines())
                # print(data)
                assert "[BCLConvert_Data]" in data
                assert "Lane,Sample_ID" in data
                if "_0" in samplesheet_name:
                    print(samplesheet_name)
                    assert "Lane,Sample_ID,index" in data
                else:
                    assert "Lane,Sample_ID,index,index2" in data
