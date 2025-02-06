import json
import os
import tempfile
import unittest
from unittest import mock

import pytest

from asf_tools.illumina.illumina_data_wrangling import generate_illumina_demux_samplesheets, check_sample_to_dataanalysis_and_index
from asf_tools.illumina.illumina_utils import IlluminaUtils

from .mocks.clarity_helper_lims_mock import ClarityHelperLimsMock
from .test_io_utils import with_temporary_folder


API_TEST_DATA = "tests/data/api/clarity"




class TestIlluminaDemux(unittest.TestCase):
    """Class for testing the generate_illumina_samplesheet tools"""

    @classmethod
    def setUpClass(cls):
        """Setup API connection"""
        data_file_path = os.path.join(API_TEST_DATA, "mock_data", "helper-data.pkl")
        cls.api = ClarityHelperLimsMock(baseuri="https://asf-claritylims.thecrick.org")
        cls.api.load_tracked_requests(data_file_path)
        cls.data_file_path = data_file_path

    @classmethod
    def tearDownClass(cls):
        """Teardown API connection"""
        cls.api.save_tracked_requests(cls.data_file_path)

    def test_check_sample_to_dataanalysis_and_index(self):
        # set up
        # info = ("22NWWMLT3", "./tests/data/illumina/22NWWMLT3/RunInfo.xml", 3)
        # file = "./tests/data/illumina/22NWWMLT3/RunInfo.xml"
        # output_path = "test_info_22NWWMLT3_1.csv"

        file = "./tests/data/illumina/22NWYFLT3/RunInfo.xml"
        output_path = "test_info_22NWYFLT3_1.csv"

        # Test
        check_sample_to_dataanalysis_and_index(self.api, file, output_path)

        raise ValueError


    # def test_generate_illumina_demux_samplesheets_general(self):
    #     """
    #     Pass real run ID with bulk/non-singlecell samples, check that a samplesheet is generated and its content
    #     """

    #     # Set up
    #     file = "./tests/data/illumina/22NWWGLT3/RunInfo.xml"
    #     # create output files paths
    #     tmp_samplesheet_file_path = os.path.join("22NWWGLT3_samplesheet_8_8.csv")
    #     tmp_bclconfig_file_path = os.path.join("bcl_config_22NWWGLT3.json")

    #     # Test
    #     generate_illumina_demux_samplesheets(self.api, file, ".")

    #     # Assert
    #     self.assertTrue(os.path.exists(tmp_samplesheet_file_path))
    #     self.assertTrue(os.path.exists(tmp_bclconfig_file_path))

    #     # Check the content of the files
    #     with open(tmp_samplesheet_file_path, "r") as file:
    #         data = "".join(file.readlines())
    #         self.assertTrue("[BCLConvert_Data]" in data)
    #     with open(tmp_bclconfig_file_path, "r") as file:
    #         config_json = json.load(file)
    #         self.assertTrue("Header" in config_json)

    @with_temporary_folder
    def test_generate_illumina_demux_samplesheets_bulk(self, tmp_path):
        """
        Pass real run ID with bulk/non-singlecell samples, check that a samplesheet is generated and its content
        """

        # Set up
        file = "./tests/data/illumina/22NWWGLT3/RunInfo.xml"
        # create output files paths
        tmp_samplesheet_file_path = os.path.join(tmp_path, "22NWWGLT3_samplesheet_8_8.csv")
        tmp_bclconfig_file_path = os.path.join(tmp_path, "bcl_config_22NWWGLT3.json")

        # Test
        generate_illumina_demux_samplesheets(self.api, file, tmp_path)

        # Assert
        self.assertTrue(os.path.exists(tmp_samplesheet_file_path))
        self.assertTrue(os.path.exists(tmp_bclconfig_file_path))

        # Check the content of the files
        with open(tmp_samplesheet_file_path, "r") as file:
            data = "".join(file.readlines())
            self.assertTrue("[BCLConvert_Data]" in data)
        with open(tmp_bclconfig_file_path, "r") as file:
            config_json = json.load(file)
            self.assertTrue("Header" in config_json)

    #############
    # flowcell_id = 22NWWGLT3
    # samples_all_info = {'WAR6617A1': {'sample_name': 'B_LTX_160_BS_GL_BCPP', 'group': 'swantonc', 'user': 'sophie.ward', 'project_id': 'DN23378', 'project_limsid': 'WAR6617', 'project_type': 'WGS', 'reference_genome': 'Homo sapiens', 'data_analysis_type': 'None', 'barcode': '015 NEBNext G2 S716-S559 (CGAATTGC-GTAAGGTG)', 'lanes': ['1', '2', '3', '4', '5', '6', '7', '8']}, 'WAR6617A2': {'sample_name': 'B_LTX_160_SU_T1-R3_BCPP', 'group': 'swantonc', 'user': 'sophie.ward', 'project_id': 'DN23378', 'project_limsid': 'WAR6617', 'project_type': 'WGS', 'reference_genome': 'Homo sapiens', 'data_analysis_type': 'None', 'barcode': '016 NEBNext H2 S708-S521 (GGAAGAGA-CGAGAGAA)', 'lanes': ['1', '2', '3', '4', '5', '6', '7', '8']}, 'WAR6617A5': {'sample_name': 'B_LTX_160_BS_GL_WCPP', 'group': 'swantonc', 'user': 'sophie.ward', 'project_id': 'DN23378', 'project_limsid': 'WAR6617', 'project_type': 'WGS', 'reference_genome': 'Homo sapiens', 'data_analysis_type': 'None', 'barcode': 'WM Custom 15 (ACTTGACT-AACGAACT)', 'lanes': ['1', '2', '3', '4', '5', '6', '7', '8']}, 'WAR6617A6': {'sample_name': 'B_LTX_160_SU_T1-R3_WCPP', 'group': 'swantonc', 'user': 'sophie.ward', 'project_id': 'DN23378', 'project_limsid': 'WAR6617', 'project_type': 'WGS', 'reference_genome': 'Homo sapiens', 'data_analysis_type': 'None', 'barcode': 'WM Custom 16 (TCTTCTCG-TATCTCAT)', 'lanes': ['1', '2', '3', '4', '5', '6', '7', '8']}}
    # sample_and_index_dict = {'WAR6617A1': {'index': 'CGAATTGC', 'index2': 'GTAAGGTG'}, 'WAR6617A2': {'index': 'GGAAGAGA', 'index2': 'CGAGAGAA'}, 'WAR6617A5': {'index': 'ACTTGACT', 'index2': 'AACGAACT'}, 'WAR6617A6': {'index': 'TCTTCTCG', 'index2': 'TATCTCAT'}}
    # config_json = {'Header': {'FileFormatVersion': 2, 'InstrumentPlatform': 'NovaSeqX', 'RunName': '22NWWGLT3'}, 'BCLConvert_Settings': {'SoftwareVersion': '4.2.7', 'FastqCompressionFormat': 'gzip'}}
    # reads_dict = {'run_id': '20241105_LH00442_0065_B22NWWGLT3', 'end_type': 'PE', 'reads': [{'read': 'Read 1', 'num_cycles': '151 Seq'}, {'read': 'Read 2', 'num_cycles': '8 Seq'}, {'read': 'Read 3', 'num_cycles': '8 Seq'}, {'read': 'Read 4', 'num_cycles': '151 Seq'}]}
    # project_type = WGS
    # filtered_samples = {'WAR6617A1': {'index': 'CGAATTGC', 'index2': 'GTAAGGTG'}, 'WAR6617A2': {'index': 'GGAAGAGA', 'index2': 'CGAGAGAA'}, 'WAR6617A5': {'index': 'ACTTGACT', 'index2': 'AACGAACT'}, 'WAR6617A6': {'index': 'TCTTCTCG', 'index2': 'TATCTCAT'}}
    # other_samples = {'WAR6617A1': {'index': 'CGAATTGC', 'index2': 'GTAAGGTG'}, 'WAR6617A2': {'index': 'GGAAGAGA', 'index2': 'CGAGAGAA'}, 'WAR6617A5': {'index': 'ACTTGACT', 'index2': 'AACGAACT'}, 'WAR6617A6': {'index': 'TCTTCTCG', 'index2': 'TATCTCAT'}}
    # split_samples_by_indexlength = [{'index_length': (8, 8), 'samples': ['WAR6617A1', 'WAR6617A2', 'WAR6617A5', 'WAR6617A6']}]
    # filtered_samples -> run after the indexing commands
    # filtered_samples = {'WAR6617A1': {'Lane': ['1', '2', '3', '4', '5', '6', '7', '8'], 'Sample_ID': 'WAR6617A1', 'index': 'CGAATTGC', 'index2': 'GTAAGGTG'}, 'WAR6617A2': {'Lane': ['1', '2', '3', '4', '5', '6', '7', '8'], 'Sample_ID': 'WAR6617A2', 'index': 'GGAAGAGA', 'index2': 'CGAGAGAA'}, 'WAR6617A5': {'Lane': ['1', '2', '3', '4', '5', '6', '7', '8'], 'Sample_ID': 'WAR6617A5', 'index': 'ACTTGACT', 'index2': 'AACGAACT'}, 'WAR6617A6': {'Lane': ['1', '2', '3', '4', '5', '6', '7', '8'], 'Sample_ID': 'WAR6617A6', 'index': 'TCTTCTCG', 'index2': 'TATCTCAT'}}
    # for each sample:
    # index_string = CGAATTGC
    # index2_string = GTAAGGTG
    # override_string = Y151;I8N0;I8N0;Y151
    # samplesheet_name = 22NWWGLT3_samplesheet_8_8
    # [151, 8, 8, 151]

    @with_temporary_folder
    def test_generate_illumina_demux_samplesheets_singlecell(self, tmp_path):
        """
        Pass real run ID with singlecell samples, check that a samplesheet is generated and its content
        """

        # Set up
        file = "./tests/data/illumina/22T3M3LT3/RunInfo.xml"
        # create output files paths
        tmp_samplesheet_file_path = os.path.join(tmp_path, "22T3M3LT3_samplesheet_singlecell.csv")
        tmp_bclconfig_file_path = os.path.join(tmp_path, "bcl_config_22T3M3LT3.json")

        # Test
        generate_illumina_demux_samplesheets(self.api, file, tmp_path)

        # Assert
        self.assertTrue(os.path.exists(tmp_samplesheet_file_path))
        self.assertTrue(os.path.exists(tmp_bclconfig_file_path))

        # Check the content of the files
        with open(tmp_samplesheet_file_path, "r") as file:
            data = "".join(file.readlines())
            self.assertTrue("[BCLConvert_Data]" in data)
        with open(tmp_bclconfig_file_path, "r") as file:
            config_json = json.load(file)
            self.assertTrue("Header" in config_json)

    @with_temporary_folder
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
        self.assertTrue(os.path.exists(tmp_samplesheet_file_path))
        self.assertTrue(os.path.exists(tmp_bclconfig_file_path))

        # Check the content of the files
        with open(tmp_samplesheet_file_path, "r") as file:
            data = "".join(file.readlines())
            self.assertTrue("[BCLConvert_Data]" in data)
            self.assertTrue("Lane,Sample_ID,index,index2" in data)
            self.assertTrue("CAACCTAG,AGGTCTGT" in data)
        with open(tmp_bclconfig_file_path, "r") as file:
            config_json = json.load(file)
            self.assertTrue("Header" in config_json)

    @with_temporary_folder
    def test_generate_illumina_demux_samplesheets_mix(self, tmp_path):
        """
        Pass real run ID with singlecell samples, check that a samplesheet is generated and its content
        """

        # Set up
        iu = IlluminaUtils()
        run_info_path = "./tests/data/illumina/22NWWGLT3/RunInfo.xml"
        mock_sample_info = "./tests/data/api/clarity/mock_data/22NWWGLT3_sample_info_mock.json"

        # Create output file paths
        tmp_samplesheet_file_path_bulk = os.path.join(tmp_path, "22NWWGLT3_samplesheet_8_8.csv")
        tmp_samplesheet_file_path_atac = os.path.join(tmp_path, "22NWWGLT3_samplesheet_atac.csv")
        tmp_samplesheet_file_path_sc = os.path.join(tmp_path, "22NWWGLT3_samplesheet_singlecell.csv")
        tmp_samplesheet_file_path_general = os.path.join(tmp_path, "22NWWGLT3_samplesheet.csv")
        tmp_bclconfig_file_path = os.path.join(tmp_path, "bcl_config_22NWWGLT3.json")

        # Extract mocked sample info from the json file
        # Load the content of the JSON file into the 'info' variable
        with open(mock_sample_info, "r") as json_file:
            json_info = json.load(json_file)
        with mock.patch("asf_tools.api.clarity.clarity_helper_lims.ClarityHelperLims") as MockClarityHelperLims:
            # Create a mock instance of ClarityHelperLims
            mock_cl = MockClarityHelperLims.return_value
            mock_cl.collect_samplesheet_info.return_value = json_info

            # Test
            generate_illumina_demux_samplesheets(mock_cl, run_info_path, tmp_path)

            # Assert
            self.assertTrue(os.path.exists(tmp_bclconfig_file_path))
            self.assertTrue(os.path.exists(tmp_samplesheet_file_path_general))
            self.assertTrue(os.path.exists(tmp_samplesheet_file_path_bulk))
            self.assertTrue(os.path.exists(tmp_samplesheet_file_path_atac))
            self.assertTrue(os.path.exists(tmp_samplesheet_file_path_sc))

            # Check the content of the files
            with open(tmp_samplesheet_file_path_bulk, "r") as file:
                data = "".join(file.readlines())
                self.assertTrue("[BCLConvert_Data]" in data)
                self.assertTrue("Lane,Sample_ID,index,index2" in data)
            with open(tmp_samplesheet_file_path_general, "r") as file:
                data = "".join(file.readlines())
                self.assertTrue("[BCLConvert_Data]" in data)
                self.assertTrue("Lane,Sample_ID,index,index2" in data)
            with open(tmp_bclconfig_file_path, "r") as file:
                config_json = json.load(file)
                self.assertTrue("Header" in config_json)
            # Check the content of the files
            with open(tmp_samplesheet_file_path_atac, "r") as file:
                data = "".join(file.readlines())
                self.assertTrue("WAR6617A5" in data)
                self.assertTrue("Lane,Sample_ID,index,index2" in data)
                # print(data)

            # Check the number of samples for each samplesheet
            samples_general = iu.count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path_general, "Sample_ID")
            samples_bulk = iu.count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path_bulk, "Sample_ID")
            # print(samples_bulk)
            samples_sc = iu.count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path_sc, "Sample_ID")
            samples_atac = iu.count_samples_in_bcl_samplesheet(tmp_samplesheet_file_path_atac, "Sample_ID")

            expected_unique_samples_entries_bulk = 15  # 5 samples
            expected_unique_samples_entries_sc = 33  # 8 samples
            expected_unique_samples_entries_atac = 60  # 11 samples
            expected_unique_samples_entries_general = 108

            assert samples_general == expected_unique_samples_entries_general
            assert samples_bulk == expected_unique_samples_entries_bulk
            assert samples_sc == expected_unique_samples_entries_sc
            assert samples_atac == expected_unique_samples_entries_atac


class TestIlluminaDemuxWithFixtures:
    """Class for testing the generate_illumina_samplesheet tools"""

    @pytest.fixture(scope="class")
    def api(self, request):
        """Setup API connection"""
        data_file_path = os.path.join(API_TEST_DATA, "mock_data", "helper-data.pkl")
        lims = ClarityHelperLimsMock(baseuri="https://asf-claritylims.thecrick.org")
        lims.load_tracked_requests(data_file_path)
        request.addfinalizer(lambda: lims.save_tracked_requests(data_file_path))
        yield lims

    @pytest.fixture(scope="function", autouse=True)
    def temporary_folder(self):
        """
        Function-level fixture that creates a temporary folder for each test.
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Attach to the test instance
            self.tmp_path = tmpdirname  # pylint: disable=attribute-defined-outside-init
            yield

    @pytest.mark.parametrize(
        "flowcell_id,runinfo_file,samplesheet_count",
        [
            ("22NWYFLT3", "./tests/data/illumina/22NWYFLT3/RunInfo.xml", 1),
            ("22NWWMLT3", "./tests/data/illumina/22NWWMLT3/RunInfo.xml", 3),
            ("22G57KLT4", "./tests/data/illumina/22G57KLT4/RunInfo.xml", 2),  # 1 general samplesheet, 1 project specific samplesheet
        ],
    )
    def test_generate_illumina_demux_samplesheets_withfixtures(self, api, flowcell_id, runinfo_file, samplesheet_count):
        """
        Pass real runs with a mix of samples with different project types and/or index length. Check that a samplesheet are generated, how many and their content
        """
        # Set up
        # create output files paths
        bclconfig_name = "bcl_config_" + flowcell_id + ".json"
        tmp_bclconfig_file_path = os.path.join(self.tmp_path, bclconfig_name)

        # Test
        generate_illumina_demux_samplesheets(api, runinfo_file, self.tmp_path)

        # Assert
        assert os.path.exists(tmp_bclconfig_file_path)

        # Check the content of the files
        with open(tmp_bclconfig_file_path, "r") as file:
            config_json = json.load(file)
            assert "Header" in config_json

        # print(os.listdir(self.tmp_path))
        # Verify the number of SampleSheet files
        samplesheet_files = [f for f in os.listdir(self.tmp_path) if "samplesheet" in f.lower() and os.path.isfile(os.path.join(self.tmp_path, f))]
        print(samplesheet_files)
        assert len(samplesheet_files) == samplesheet_count

        general_samplesheet_name = os.path.join(self.tmp_path, flowcell_id + "_samplesheet.csv")
        # print(general_samplesheet_name)
        # Check the content of the files
        with open(general_samplesheet_name, "r") as file:
            data = "".join(file.readlines())
            # print(data)
            assert "[BCLConvert_Data]" in data
            assert "Lane,Sample_ID" in data
            assert "Lane,Sample_ID,index,index2" in data

        # ['22NWYFLT3_samplesheet.csv']
        # ['22NWWMLT3_samplesheet_singlecell.csv', '22NWWMLT3_samplesheet.csv', '22NWWMLT3_samplesheet_atac.csv']
        # ['22G57KLT4_samplesheet.csv', '22G57KLT4_samplesheet_8_8.csv']
