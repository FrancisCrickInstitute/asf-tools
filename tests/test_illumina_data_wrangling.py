import json
import os
import tempfile
import unittest

import pytest

from asf_tools.illumina.illumina_data_wrangling import generate_illumina_demux_samplesheets

from .mocks.clarity_helper_lims_mock import ClarityHelperLimsMock
from .test_io_utils import with_temporary_folder


API_TEST_DATA = "tests/data/api/clarity"

# def test_generate_illumina_demux1():
#     # Set up
#     file = "./tests/data/illumina/22NWWGLT3/RunInfo.xml"

#     # Test
#     generate_illumina_demux_samplesheets(file, ".")


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
        file = "./tests/data/illumina/HWNCWDMXY/RunInfo.xml"
        # create output files paths
        tmp_samplesheet_file_path = os.path.join(tmp_path, "HWNCWDMXY_samplesheet_dlp.csv")
        tmp_bclconfig_file_path = os.path.join(tmp_path, "bcl_config_HWNCWDMXY.json")

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

    # @with_temporary_folder
    # def test_generate_illumina_dlp_samplesheets_bulk(self, tmp_path):
    #     """
    #     Pass real run ID with bulk/non-singlecell samples, check that a samplesheet is generated and its content
    #     """

    #     # Set up
    #     file = "./tests/data/illumina/22NWWGLT3/RunInfo.xml"
    #     # create output files paths
    #     tmp_samplesheet_file_path = os.path.join(tmp_path, "22NWWGLT3_samplesheet_8_8.csv")
    #     tmp_bclconfig_file_path = os.path.join(tmp_path, "bcl_config_22NWWGLT3.json")

    #     # Test
    #     generate_illumina_demux_samplesheets(self.api, file, tmp_path)

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
        [("22NWWMLT3", "./tests/data/illumina/22NWWMLT3/RunInfo.xml", 2), ("22NWYFLT3", "./tests/data/illumina/22NWYFLT3/RunInfo.xml", 1)],
    )
    def test_generate_illumina_demux_samplesheets_withfixtures(self, api, flowcell_id, runinfo_file, samplesheet_count):
        # Set up
        # create output files paths
        samplesheet_file_name = flowcell_id + "_samplesheet_10_10.csv"
        bclconfig_name = "bcl_config_" + flowcell_id + "json"
        tmp_samplesheet_file_path = os.path.join(self.tmp_path, samplesheet_file_name)
        tmp_bclconfig_file_path = os.path.join(self.tmp_path, bclconfig_name)

        # Test
        generate_illumina_demux_samplesheets(api, runinfo_file, self.tmp_path)

        # Assert
        assert os.path.exists(tmp_samplesheet_file_path)
        assert os.path.exists(tmp_bclconfig_file_path)

        # Check the content of the files
        with open(tmp_samplesheet_file_path, "r") as file:
            data = "".join(file.readlines())
            assert "[BCLConvert_Data]" in data
        with open(tmp_bclconfig_file_path, "r") as file:
            config_json = json.load(file)
            assert "Header" in config_json


###########################################
# import unittest
# from unittest.mock import Mock, patch, call
# import json

# class TestOverallWorkflow(unittest.TestCase):
#     def setUp(self):
#         # Mock the classes
#         self.iu = Mock(spec=IlluminaUtils)
#         self.cl = Mock(spec=ClarityHelperLims)

#         # Mock input values
#         self.runinfo_file = "RunInfo.xml"
#         self.bcl_config_path = None
#         self.flowcell_id = "FC001"

#         # Example sample data
#         self.samples_all_info = [
#             {"sample_id": "sample1", "project_type": "DLP"},
#             {"sample_id": "sample2", "project_type": "single_cell"},
#             {"sample_id": "sample3", "project_type": "bulk"},
#         ]

#         self.sample_and_index_dict = {
#             "sample1": {"index": "ATGC"},
#             "sample2": {"index": "CGTA"},
#             "sample3": {"index": "GCTA"},
#         }

#         # Mock config JSON
#         self.mock_config_json = {
#             "Header": {"Date": "2024-11-18"},
#             "BCLConvert_Settings": {"OverrideCycles": "Y151;I8;I8;Y151"},
#         }

#         # Expected groupings
#         self.split_samples_by_projecttype = {
#             "DLP": ["sample1"],
#             "single_cell": ["sample2"],
#             "bulk": ["sample3"],
#         }

#     @patch("builtins.open", create=True)
#     @patch("json.load")
#     @patch("json.dump")
#     def test_overall_workflow(self, mock_json_dump, mock_json_load, mock_open):
#         # Mock method return values
#         self.iu.extract_illumina_runid_fromxml.return_value = self.flowcell_id
#         self.cl.collect_samplesheet_info.return_value = self.samples_all_info
#         self.iu.reformat_barcode.return_value = self.sample_and_index_dict
#         self.iu.filter_runinfo.return_value = {"machine": "NovaSeq"}
#         self.iu.generate_bclconfig.return_value = self.mock_config_json
#         self.iu.runinfo_xml_to_dict.return_value = {"Reads": "MockReads"}
#         self.iu.filter_readinfo.return_value = {"Read1": 151, "Index1": 8, "Index2": 8}
#         self.iu.group_samples_by_dictkey.return_value = self.split_samples_by_projecttype
#         self.iu.group_samples_by_index_length.return_value = [
#             {"index_length": [8, 0], "samples": ["sample3"]}
#         ]
#         self.iu.extract_cycle_fromxml.return_value = [151, 8, 8, 151]

#         # Simulate opening a BCL config file
#         mock_json_load.return_value = self.mock_config_json

#         # Run the overall workflow
#         # Ensure the workflow runs without errors or exceptions
#         dlp_samples = {}
#         single_cell_samples = {}
#         other_samples = {}

#         for project_type, samples in self.split_samples_by_projecttype.items():
#             filtered_samples = {sample: self.sample_and_index_dict[sample] for sample in samples}

#             if "DLP" in project_type:
#                 dlp_samples.update(filtered_samples)

#             elif "single_cell" in project_type:
#                 single_cell_samples.update(filtered_samples)

#             else:
#                 other_samples.update(filtered_samples)

#         # Assertions
#         # Validate DLP samples were correctly grouped
#         self.assertEqual(dlp_samples, {"sample1": {"index": "ATGC"}})

#         # Validate single cell samples were correctly grouped
#         self.assertEqual(single_cell_samples, {"sample2": {"index": "CGTA"}})

#         # Validate bulk samples were correctly grouped
#         self.assertEqual(other_samples, {"sample3": {"index": "GCTA"}})

#         # Verify samplesheet generation for single cell
#         self.iu.generate_bcl_samplesheet.assert_any_call(
#             self.mock_config_json["Header"],
#             {"Read1": 151, "Index1": 8, "Index2": 8},
#             self.mock_config_json["BCLConvert_Settings"],
#             {"sample2": {"index": "CGTA"}},
#             f"{self.flowcell_id}_samplesheet_10X_",
#         )

#         # Verify samplesheet generation for bulk samples
#         self.iu.generate_bcl_samplesheet.assert_any_call(
#             self.mock_config_json["Header"],
#             {"Read1": 151, "Index1": 8, "Index2": 8},
#             self.mock_config_json["BCLConvert_Settings"],
#             {"sample3": {"index": "GCTA"}},
#             f"{self.flowcell_id}samplesheet_8_0",
#         )

#         # Verify the OverrideCycles generation logic
#         self.iu.generate_overridecycle_string.assert_called_with(
#             "GCTA", 8, 151
#         )

#         # Check the number of samplesheets created
#         self.assertEqual(self.iu.generate_bcl_samplesheet.call_count, 2)


# if __name__ == "__main__":
#     unittest.main()
