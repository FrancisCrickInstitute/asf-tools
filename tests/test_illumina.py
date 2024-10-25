"""
Tests covering the data_transfer module
"""

import csv
import io
import os
import tempfile
import unittest
from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock, mock_open, patch
from xml.parsers.expat import ExpatError

import pytest

from asf_tools.illumina.illumina_utils import IlluminaUtils


class TestIlluminaUtils(unittest.TestCase):
    """Class for parse_runinfo tests"""

    def test_runinfo_xml_to_dict_filenotexist(self):
        """
        Pass a file that does not exist
        """

        # Set up
        iu = IlluminaUtils()
        invalid_path = "file_does_not_exist"

        # Test and Assert
        with self.assertRaises(FileNotFoundError):
            iu.runinfo_xml_to_dict(invalid_path)

    def test_runinfo_xml_to_dict_isnotxml(self):
        """
        Pass a file that is not XML
        """

        # Set up
        iu = IlluminaUtils()
        invalid_file = "./tests/data/illumina/dummy.txt"

        # Test and Assert
        with self.assertRaises(ExpatError):
            iu.runinfo_xml_to_dict(invalid_file)

    def test_runinfo_xml_to_dict_isinvalid(self):
        """
        Pass a xml file with compromised content
        """

        # Set up
        iu = IlluminaUtils()
        invalid_file = "./tests/data/illumina/fake_RunInfo.xml"

        # Test and Assert
        with self.assertRaises(ExpatError):
            iu.runinfo_xml_to_dict(invalid_file)

    def test_find_key_recursively_none(self):
        """
        Pass None to method
        """

        # Set up
        iu = IlluminaUtils()

        # Test and Assert
        with self.assertRaises(ValueError):
            iu.find_key_recursively(None, "None")

    def test_find_key_recursively_emptytarget(self):
        """
        Pass empty target string to method
        """

        # Set up
        iu = IlluminaUtils()
        file = "./tests/data/illumina/RunInfo.xml"
        xml_dict = iu.runinfo_xml_to_dict(file)

        # Test and Assert
        with self.assertRaises(ValueError):
            iu.find_key_recursively(xml_dict, "")

    def test_extract_matching_item_from_dict_returnnone(self):
        """
        Pass empty list to method
        """

        # Set up
        iu = IlluminaUtils()
        file = "./tests/data/illumina/RunInfo.xml"
        xml_dict = iu.runinfo_xml_to_dict(file)

        # Test and Assert
        with self.assertRaises(TypeError):
            iu.extract_matching_item_from_dict(xml_dict, "info_not_in_file")

    def test_filter_runinfo_machinenotexist(self):
        """
        Tests the `filter_runinfo` method for handling an unrecognized instrument.

        This test method sets up a mock RunInfo dictionary where the instrument
        name does not match any of the predefined patterns in the `filter_runinfo` method.
        The test verifies that the method raises a `ValueError` when it encounters an
        unrecognized instrument.

        The test ensures that `filter_runinfo` properly handles invalid or unknown
        instrument names by raising the appropriate exception.

        Assertions:
            - A `ValueError` is raised when the instrument is not recognized.

        Raises:
            ValueError: If the instrument type does not match any predefined patterns.
        """
        # Set up
        iu = IlluminaUtils()
        xml_dict = {
            "@Version": "6",
            "Run": {
                "@Id": "20240711_LH00442_0033_A22MKK5LT3",
                "@Number": "33",
                "Flowcell": "22MKK5LT3",
                "Instrument": "instrument_not_valid",
                "Date": "2024-07-11T18:44:29Z",
                "Reads": {"Read": [{"@Number": "1", "@NumCycles": "151", "@IsIndexedRead": "N", "@IsReverseComplement": "N"}]},
                "FlowcellLayout": {
                    "@LaneCount": "8",
                },
            },
        }

        # Test and Assert
        with self.assertRaises(ValueError):
            iu.filter_runinfo(xml_dict)

    def test_filter_runinfo_isvalid(self):
        """
        Tests the `filter_runinfo` method for correct functionality.

        This test method sets up a mock RunInfo dictionary representing an XML structure
        and verifies that the `filter_runinfo` method processes this input correctly.
        The test compares the output of `filter_runinfo` against an expected dictionary
        that includes the current date and time, run ID, instrument, and machine type.

        The test checks that the `filter_runinfo` method correctly identifies the machine
        type based on the instrument pattern and returns the expected structured dictionary.

        Assertions:
            - The output of `filter_runinfo` should match the expected dictionary.

        Raises:
            AssertionError: If the output does not match the expected dictionary.
        """
        # Set up
        iu = IlluminaUtils()
        xml_dict = {
            "@Version": "6",
            "Run": {
                "@Id": "20240711_LH00442_0033_A22MKK5LT3",
                "@Number": "33",
                "Flowcell": "22MKK5LT3",
                "Instrument": "LH00442",
                "Date": "2024-07-11T18:44:29Z",
                "Reads": {
                    "Read": [
                        {"@Number": "1", "@NumCycles": "151", "@IsIndexedRead": "N", "@IsReverseComplement": "N"},
                        {"@Number": "2", "@NumCycles": "10", "@IsIndexedRead": "Y", "@IsReverseComplement": "N"},
                        {"@Number": "3", "@NumCycles": "10", "@IsIndexedRead": "Y", "@IsReverseComplement": "Y"},
                        {"@Number": "4", "@NumCycles": "151", "@IsIndexedRead": "N", "@IsReverseComplement": "N"},
                    ]
                },
                "FlowcellLayout": {
                    "@LaneCount": "8",
                    "@SurfaceCount": "2",
                    "@SwathCount": "2",
                    "@TileCount": "98",
                    "TileSet": {
                        "@TileNamingConvention": "FourDigit",
                        "Tiles": {
                            "Tile": [
                                "1_1101",
                            ]
                        },
                    },
                },
                "ImageDimensions": {"@Width": "5120", "@Height": "2879"},
                "ImageChannels": {"Name": ["blue", "green"]},
            },
        }

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expected_dict = {
            "current_date": current_datetime,
            "run_id": "20240711_LH00442_0033_A22MKK5LT3",
            "instrument": "LH00442",
            "machine": "NovaSeqX",
            "lane": "8",
        }

        # Test
        run_info = iu.filter_runinfo(xml_dict)
        # print(run_info)

        # Assert
        assert run_info == expected_dict

    def test_extract_illumina_runid_fromxml(self):
        """
        Pass a valid XML file and test expected RunID values from the dictionary output
        """
        # Set up
        iu = IlluminaUtils()
        file = "./tests/data/illumina/RunInfo.xml"
        flowcell_runid = "22MKK5LT3"

        # Test
        run_info = iu.extract_illumina_runid_fromxml(file)
        print(run_info)

        # Assert
        assert run_info == flowcell_runid

    def test_merge_runinfo_dict_fromfile(self):
        """
        Pass a valid XML file and test expected values in the dictionary output
        """
        # Set up
        iu = IlluminaUtils()
        file = "./tests/data/illumina/RunInfo.xml"

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expected_dict = {
            "run_id": "20240711_LH00442_0033_A22MKK5LT3",
            "end_type": "PE",
            "reads": [
                {"read": "Read 1", "num_cycles": "151 Seq"},
                {"read": "Read 2", "num_cycles": "10 Seq"},
                {"read": "Read 3", "num_cycles": "10 Seq"},
                {"read": "Read 4", "num_cycles": "151 Seq"},
            ],
            "current_date": current_datetime,
            "instrument": "LH00442",
            "machine": "NovaSeqX",
            "lane": "8",
        }

        # Test
        filtered_info = iu.merge_runinfo_dict_fromfile(file)
        # print(filtered_info)

        # Assert
        assert filtered_info == expected_dict

    def test_generate_overridecycle_string_indexnone(self):
        """
        Pass empty target string to method
        """

        # Set up
        iu = IlluminaUtils()

        # Test and Assert
        with self.assertRaises(TypeError):
            iu.generate_overridecycle_string("", 10, 8)
        with self.assertRaises(TypeError):
            iu.generate_overridecycle_string(None, 10, 8)

    def test_generate_overridecycle_string_integernone(self):
        """
        Pass empty integer value to method
        """

        # Set up
        iu = IlluminaUtils()

        # Test and Assert
        with self.assertRaises(TypeError):
            iu.generate_overridecycle_string("Value", None, 8)
        with self.assertRaises(TypeError):
            iu.generate_overridecycle_string("Value", 10, None)
        with self.assertRaises(TypeError):
            iu.generate_overridecycle_string("Value", 10)

    def test_generate_overridecycle_string_negativeinteger(self):
        """
        Pass a negative integer to method
        """

        # Set up
        iu = IlluminaUtils()

        # Test and Assert
        with self.assertRaises(TypeError):
            iu.generate_overridecycle_string("Value", 10, -8)

        with self.assertRaises(TypeError):
            iu.generate_overridecycle_string("Value", -10, 8)

    def test_generate_overridecycle_string_isvalid(self):
        """
        Pass valid inputs to method
        """

        # Set up
        iu = IlluminaUtils()
        expected = "Y151;I8N2;I8N2;Y151,"

        # Test
        result = iu.generate_overridecycle_string("AATTCCGG", 10, 151)

        # Assert
        assert result == expected

    # def test_convert_to_bcl_compliant_filenotexist(self):
    #     """
    #     Pass a file that does not exist
    #     """

    #     # Set up
    #     iu = IlluminaUtils()
    #     invalid_path = "file_does_not_exist"
    #     output_file_name = "file"
    #     bcl_settings_dict = {"settings": "fake_settings"}
    #     bcl_data_dict = {"data": "fake_data"}

    #     # Test and Assert
    #     with self.assertRaises(FileNotFoundError):
    #         iu.convert_to_bcl_compliant(invalid_path, output_file_name, bcl_settings_dict, bcl_data_dict)

    #         # def test_extract_top_unknown_barcode_from_html_filenotexist(self):
    #         #     """
    #         #     Pass a file that does not exist
    #         #     """

    #         #     # Set up
    #         #     iu = IlluminaUtils()
    #         #     invalid_path = "file_does_not_exist"

    #         #     # Test and Assert
    #         #     with self.assertRaises(FileNotFoundError):
    #         iu.extract_top_unknown_barcode_from_html(invalid_path)

    # def test_extract_top_unknown_barcode_from_html_fileinvalid(self):
    #     """
    #     Pass a file that is not html
    #     """

    #     # Set up
    #     iu = IlluminaUtils()
    #     invalid_input = "./tests/data/illumina/dummy.txt"

    #     # Test and Assert
    #     with self.assertRaises(ValueError):
    #         iu.extract_top_unknown_barcode_from_html(invalid_input)


class TestIlluminaUtilsWithFixtures:
    """Class for IlluminaUtils tests with fixtures"""

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
        "file,expected_dict",
        [
            (
                "./tests/data/illumina/RunInfo.xml",
                {
                    "RunInfo": {
                        "@Version": "6",
                        "Run": {
                            "@Id": "20240711_LH00442_0033_A22MKK5LT3",
                            "@Number": "33",
                            "Flowcell": "22MKK5LT3",
                            "Instrument": "LH00442",
                            "Date": "2024-07-11T18:44:29Z",
                            "Reads": {
                                "Read": [
                                    {"@Number": "1", "@NumCycles": "151", "@IsIndexedRead": "N", "@IsReverseComplement": "N"},
                                    {"@Number": "2", "@NumCycles": "10", "@IsIndexedRead": "Y", "@IsReverseComplement": "N"},
                                    {"@Number": "3", "@NumCycles": "10", "@IsIndexedRead": "Y", "@IsReverseComplement": "Y"},
                                    {"@Number": "4", "@NumCycles": "151", "@IsIndexedRead": "N", "@IsReverseComplement": "N"},
                                ]
                            },
                            "FlowcellLayout": {
                                "@LaneCount": "8",
                                "@SurfaceCount": "2",
                                "@SwathCount": "2",
                                "@TileCount": "98",
                                "TileSet": {
                                    "@TileNamingConvention": "FourDigit",
                                    "Tiles": {
                                        "Tile": [
                                            "1_1101",
                                            "2_1101",
                                            "3_1101",
                                            "4_1101",
                                            "5_1101",
                                            "6_1232",
                                            "7_1101",
                                            "8_1101",
                                            "1_2298",
                                            "2_2101",
                                            "3_2101",
                                            "4_2101",
                                            "5_2101",
                                            "6_2101",
                                            "7_2101",
                                            "8_2101",
                                        ]
                                    },
                                },
                            },
                            "ImageDimensions": {"@Width": "5120", "@Height": "2879"},
                            "ImageChannels": {"Name": ["blue", "green"]},
                        },
                    }
                },
            )
        ],
    )
    def test_runinfo_xml_to_dict_isvalid(self, file, expected_dict):
        """
        Pass a valid XML file and test expected values in the dictionary output
        """

        # Set up
        iu = IlluminaUtils()

        # Test
        xml_info = iu.runinfo_xml_to_dict(file)
        print(xml_info)

        # Assert
        assert xml_info == expected_dict

    @pytest.mark.parametrize(
        "dic,expected_list",
        [
            ({"run": {"@Id": "20240711_LH00442_0033_A22MKK5LT3"}}, ["20240711_LH00442_0033_A22MKK5LT3"]),
            ({"run": {"other_info": {"@Id": "20240711_LH00442_0033_A22MKK5LT3"}}}, ["20240711_LH00442_0033_A22MKK5LT3"]),
        ],
    )
    def test_find_key_recursively_isvalid(self, dic, expected_list):
        """
        Pass a valid dictionary from XML file and test expected values in the output list
        """

        # Set up
        iu = IlluminaUtils()

        # Test and Assert
        list_extracted_info = iu.find_key_recursively(dic, "@Id")

        # Assert
        assert list_extracted_info == expected_list

    @pytest.mark.parametrize(
        "list_info,expected_output", [({"run": {"@Id": "20240711_LH00442_0033_A22MKK5LT3"}}, "20240711_LH00442_0033_A22MKK5LT3")]
    )
    def test_extract_matching_item_from_dict_isvalid(self, list_info, expected_output):
        """
        Pass a valid dictionary and test expected values in the output
        """

        # Set up
        iu = IlluminaUtils()

        # Test and Assert
        list_extracted_info = iu.extract_matching_item_from_dict(list_info, "@Id")

        # Assert
        assert list_extracted_info == expected_output

    @pytest.mark.parametrize(
        "file,expected_dict",
        [
            (
                "./tests/data/illumina/RunInfo.xml",
                {
                    "run_id": "20240711_LH00442_0033_A22MKK5LT3",
                    "end_type": "PE",
                    "reads": [
                        {"read": "Read 1", "num_cycles": "151 Seq"},
                        {"read": "Read 2", "num_cycles": "10 Seq"},
                        {"read": "Read 3", "num_cycles": "10 Seq"},
                        {"read": "Read 4", "num_cycles": "151 Seq"},
                    ],
                },
            )
        ],
    )
    def test_filter_readinfo_isvalid(self, file, expected_dict):
        """
        Pass a valid XML file and test expected values in the dictionary output
        """
        # Set up
        iu = IlluminaUtils()

        # Test
        xml_info = iu.runinfo_xml_to_dict(file)
        read_info = iu.filter_readinfo(xml_info)
        # print(xml_info)

        # Assert
        assert read_info == expected_dict

    @pytest.mark.parametrize(
        "dict1,dict2,expected_merged_dict",
        [
            (
                {"run_id": "20240711_LH00442_0033_A22MKK5LT3", "instrument": "LH00442"},
                {
                    "run_id": "20240711_LH00442_0033_A22MKK5LT3",
                    "reads": [{"read": "Read 1", "num_cycles": "151 Seq"}, {"read": "Read 2", "num_cycles": "10 Seq"}],
                },
                {
                    "run_id": "20240711_LH00442_0033_A22MKK5LT3",
                    "instrument": "LH00442",
                    "reads": [{"read": "Read 1", "num_cycles": "151 Seq"}, {"read": "Read 2", "num_cycles": "10 Seq"}],
                },
            )
        ],
    )
    def test_merge_dicts(self, dict1, dict2, expected_merged_dict):
        """
        Pass a two different dictionaries, merge and test expected values in the merged dictionary output
        """
        # Set up
        iu = IlluminaUtils()

        # Test
        merged_dict = iu.merge_dicts(dict1, dict2, "run_id")

        # Assert
        assert merged_dict == expected_merged_dict

    # @pytest.mark.parametrize(
    #     "header_dict,reads_dict,samples_dict",
    #     [
    #         (
    #             {"IEMFileVersion": "4", "Date": "2024-09-12", "Workflow": "GenerateFASTQ"},
    #             {"Read1Cycles": "151", "Adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
    #             {
    #                 "sample1": {"Sample_ID": "sample1", "sample_name": "test_sample_1", "index": "A001"},
    #                 "sample2": {"Sample_ID": "sample2", "index": "A002", "sample_name": "test_sample_2"},
    #             },
    #         )
    #     ],
    # )
    # def test_dict_to_illumina_v2_csv_valid(self, header_dict, reads_dict, samples_dict):
    #     """
    #     Check that the csv file is created and contains the correct data
    #     """
    #     # Set up
    #     iu = IlluminaUtils()
    #     output_file_name = os.path.join(self.tmp_path, "test_samplesheet")

    #     # Test
    #     iu.dict_to_illumina_v2_csv(header_dict, reads_dict, samples_dict, output_file_name)

    #     # Assert
    #     output_file_csv = output_file_name + ".csv"
    #     assert os.path.exists(output_file_csv)

    #     with open(output_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)

    #         # Check the header
    #         assert content[0] == ["[Header]"]
    #         assert ["IEMFileVersion", "4"] in content
    #         assert ["Date", "2024-09-12"] in content
    #         assert ["Workflow", "GenerateFASTQ"] in content

    #         # Check the reads
    #         assert ["[Reads]"] in content
    #         assert ["Read1Cycles", "151"] in content
    #         assert ["Adapter", "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"] in content

    #         # Check the sample data
    #         assert ["[Data]"] in content
    #         assert content[-3] == ["Sample_ID", "index", "sample_name"]
    #         assert content[-2] == ["sample1", "A001", "test_sample_1"]
    #         assert content[-1] == ["sample2", "A002", "test_sample_2"]

    # @pytest.mark.parametrize(
    #     "reads_dict,samples_dict",
    #     [
    #         (
    #             {"Read1Cycles": "151", "Adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
    #             {
    #                 "sample1": {"Sample_ID": "sample1", "sample_name": "test_sample_1", "index": "A001"},
    #                 "sample2": {"Sample_ID": "sample2", "index": "A002", "sample_name": "test_sample_2"},
    #             },
    #         )
    #     ],
    # )
    # def test_dict_to_illumina_v2_csv_no_header(self, reads_dict, samples_dict):
    #     """
    #     Test behavior with an empty header_dict
    #     """
    #     # Set up
    #     iu = IlluminaUtils()
    #     empty_header_dict = {}
    #     output_file_name = os.path.join(self.tmp_path, "test_samplesheet")

    #     # Test
    #     iu.dict_to_illumina_v2_csv(empty_header_dict, reads_dict, samples_dict, output_file_name)

    #     # Assert
    #     output_file_csv = output_file_name + ".csv"
    #     with open(output_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)
    #         print(content)

    #         # Ensure the samples and reads sections are present
    #         assert ["[Reads]"] in content
    #         assert ["[Data]"] in content
    #         assert content[-3] == ["Sample_ID", "index", "sample_name"]
    #         assert content[-2] == ["sample1", "A001", "test_sample_1"]
    #         assert content[-1] == ["sample2", "A002", "test_sample_2"]
    #         # Ensure that [Header] section is empty
    #         assert ["[Header]"] not in content

    # @pytest.mark.parametrize(
    #     "header_dict,samples_dict",
    #     [
    #         (
    #             {"IEMFileVersion": "4", "Date": "2024-09-12", "Workflow": "GenerateFASTQ"},
    #             {
    #                 "sample1": {"Sample_ID": "sample1", "sample_name": "test_sample_1", "index": "A001"},
    #                 "sample2": {"Sample_ID": "sample2", "index": "A002", "sample_name": "test_sample_2"},
    #             },
    #         )
    #     ],
    # )
    # def test_dict_to_illumina_v2_csv_no_reads(self, header_dict, samples_dict):
    #     """
    #     Test behavior with an empty reads_dict
    #     """
    #     # Set up
    #     iu = IlluminaUtils()
    #     empty_reads_dict = {}
    #     output_file_name = os.path.join(self.tmp_path, "test_samplesheet")

    #     # Test
    #     iu.dict_to_illumina_v2_csv(header_dict, empty_reads_dict, samples_dict, output_file_name)

    #     # Assert
    #     output_file_csv = output_file_name + ".csv"
    #     with open(output_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)
    #         print(content)

    #         # Ensure the samples and reads sections are present
    #         assert ["[Header]"] in content
    #         assert ["[Data]"] in content
    #         assert content[-3] == ["Sample_ID", "index", "sample_name"]
    #         assert content[-2] == ["sample1", "A001", "test_sample_1"]
    #         assert content[-1] == ["sample2", "A002", "test_sample_2"]
    #         # Ensure that [Reads] section is empty
    #         assert ["[Reads]"] not in content

    # @pytest.mark.parametrize(
    #     "header_dict,reads_dict",
    #     [
    #         (
    #             {"IEMFileVersion": "4", "Date": "2024-09-12", "Workflow": "GenerateFASTQ"},
    #             {"Read1Cycles": "151", "Adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
    #         )
    #     ],
    # )
    # def test_dict_to_illumina_v2_csv_no_samples(self, header_dict, reads_dict):
    #     """
    #     Test behavior with an empty samples_dict
    #     """
    #     # Set up
    #     iu = IlluminaUtils()
    #     empty_samples_dict = {}
    #     output_file_name = os.path.join(self.tmp_path, "test_samplesheet")

    #     # Test
    #     iu.dict_to_illumina_v2_csv(header_dict, reads_dict, empty_samples_dict, output_file_name)

    #     # Assert
    #     output_file_csv = output_file_name + ".csv"
    #     with open(output_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)
    #         print(content)

    #         # Ensure the header and reads sections are present
    #         assert content[0] == ["[Header]"]
    #         assert ["[Reads]"] in content
    #         # Ensure that [Data] section is empty
    #         assert ["[Data]"] not in content
    #         assert ["Sample_ID"] not in content

    # @pytest.mark.parametrize(
    #     "header_dict,reads_dict",
    #     [
    #         (
    #             {"IEMFileVersion": "4", "Date": "2024-09-12", "Workflow": "GenerateFASTQ"},
    #             {"Read1Cycles": "151", "Adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
    #         )
    #     ],
    # )
    # def test_dict_to_illumina_v2_csv_partial_sample_info(self, header_dict, reads_dict):
    #     """
    #     Test with samples missing some fields
    #     """
    #     # Set up
    #     iu = IlluminaUtils()

    #     incomplete_samples_dict = {
    #         "sample1": {"Sample_ID": "sample1", "index": "A001"},  # missing sample_name
    #         "sample2": {"Sample_ID": "sample2", "sample_name": "test_sample_2"},  # missing index
    #     }
    #     output_file_name = os.path.join(self.tmp_path, "test_samplesheet")

    #     # Test
    #     iu.dict_to_illumina_v2_csv(header_dict, reads_dict, incomplete_samples_dict, output_file_name)

    #     # Assert
    #     output_file_csv = output_file_name + ".csv"
    #     with open(output_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)
    #         print(content)

    #         # Ensure the missing fields are replaced with empty strings
    #         assert ["[Data]"] in content
    #         assert content[-3] == ["Sample_ID", "index", "sample_name"]
    #         assert content[-2] == ["sample1", "A001", ""]
    #         assert content[-1] == ["sample2", "", "test_sample_2"]

    # @pytest.mark.parametrize(
    #     "bcl_settings_dict,bcl_data_dict",
    #     [
    #         (
    #             {"SoftwareVersion": "x.y.z", "AdapterBehavior": "trim"},
    #             {
    #                 "sample1": {"Sample_ID": "sample1", "index2": "B001", "index": "A001"},
    #                 "sample2": {"Sample_ID": "sample2", "index": "A002", "index2": "B002"},
    #             },
    #         )
    #     ],
    # )
    # def test_convert_to_bcl_compliant_valid(self, bcl_settings_dict, bcl_data_dict):
    #     """
    #     Check that the csv file is created and contains the correct data
    #     """
    #     # Set up
    #     iu = IlluminaUtils()
    #     input_file = os.path.join(self.tmp_path, "test_samplesheet.csv")
    #     with open(input_file, "w", encoding="ASCII"):
    #         pass
    #     output_file_name = os.path.join(self.tmp_path, "output_file")

    #     # Test
    #     iu.convert_to_bcl_compliant(input_file, output_file_name, bcl_settings_dict, bcl_data_dict)

    #     # Assert
    #     output_file_csv = output_file_name + ".csv"
    #     assert os.path.exists(output_file_csv)

    #     with open(output_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)

    #         # Check the settings
    #         assert ["[BCLConvert_Settings]"] in content
    #         assert ["SoftwareVersion", "x.y.z"] in content
    #         assert ["AdapterBehavior", "trim"] in content

    #         # Check the data
    #         assert ["[BCLConvert_Data]"] in content
    #         assert content[-3] == ["Sample_ID", "index", "index2"]
    #         assert content[-2] == ["sample1", "A001", "B001"]
    #         assert content[-1] == ["sample2", "A002", "B002"]

    # @pytest.mark.parametrize(
    #     "bcl_data_dict",
    #     [
    #         {
    #             "sample1": {"Sample_ID": "sample1", "index2": "B001", "index": "A001"},
    #             "sample2": {"Sample_ID": "sample2", "index": "A002", "index2": "B002"},
    #         },
    #     ],
    # )
    # def test_convert_to_bcl_compliant_no_settings(self, bcl_data_dict):
    #     """
    #     Test behavior with an empty settings_dict
    #     """
    #     # Set up
    #     iu = IlluminaUtils()
    #     input_file = os.path.join(self.tmp_path, "test_samplesheet.csv")
    #     with open(input_file, "w", encoding="ASCII"):
    #         pass
    #     output_file_name = os.path.join(self.tmp_path, "output_file")
    #     empty_settings_dict = {}

    #     # Test
    #     iu.convert_to_bcl_compliant(input_file, output_file_name, empty_settings_dict, bcl_data_dict)

    #     # Assert
    #     output_file_csv = output_file_name + ".csv"
    #     with open(output_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)
    #         print(content)

    #         # Ensure that [BCLConvert_Settings] section is empty
    #         assert ["[BCLConvert_Data]"] in content
    #         assert ["[BCLConvert_Settings]"] not in content

    # @pytest.mark.parametrize(
    #     "bcl_settings_dict",
    #     [
    #         {"SoftwareVersion": "x.y.z", "AdapterBehavior": "trim"},
    #     ],
    # )
    # def test_convert_to_bcl_compliant_no_data(self, bcl_settings_dict):
    #     """
    #     Test behavior with an empty data_dict
    #     """
    #     # Set up
    #     iu = IlluminaUtils()
    #     input_file = os.path.join(self.tmp_path, "test_samplesheet.csv")
    #     with open(input_file, "w", encoding="ASCII"):
    #         pass
    #     output_file_name = os.path.join(self.tmp_path, "output_file")
    #     empty_data_dict = {}

    #     # Test
    #     iu.convert_to_bcl_compliant(input_file, output_file_name, bcl_settings_dict, empty_data_dict)

    #     # Assert
    #     output_file_csv = output_file_name + ".csv"
    #     with open(output_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)
    #         print(content)

    #         # Ensure that [BCLConvert_Data] section is empty
    #         assert ["[BCLConvert_Data]"] not in content
    #         assert ["[BCLConvert_Settings]"] in content

    # @pytest.mark.parametrize(
    #     "bcl_settings_dict,bcl_data_dict",
    #     [
    #         (
    #             {"SoftwareVersion": "x.y.z", "AdapterBehavior": "trim"},
    #             {
    #                 "sample1": {"Sample_ID": "sample1", "index2": "B001", "index": "A001"},
    #                 "sample2": {"Sample_ID": "sample2", "index": "A002", "index2": ""},
    #             },
    #         )
    #     ],
    # )
    # def test_convert_to_bcl_compliant_partial_data(self, bcl_settings_dict, bcl_data_dict):
    #     """
    #     Test behavior with an empty settings_dict
    #     """
    #     # Set up
    #     iu = IlluminaUtils()
    #     input_file = os.path.join(self.tmp_path, "test_samplesheet.csv")
    #     with open(input_file, "w", encoding="ASCII"):
    #         pass
    #     output_file_name = os.path.join(self.tmp_path, "output_file")

    #     # Test
    #     iu.convert_to_bcl_compliant(input_file, output_file_name, bcl_settings_dict, bcl_data_dict)

    #     # Assert
    #     output_file_csv = output_file_name + ".csv"
    #     with open(output_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)
    #         print(content)

    #         # Ensure that both headers exist, as expected
    #         assert ["[BCLConvert_Data]"] in content
    #         assert ["[BCLConvert_Settings]"] in content

    #         # Check the data
    #         assert content[-3] == ["Sample_ID", "index", "index2"]
    #         assert content[-2] == ["sample1", "A001", "B001"]
    #         assert content[-1] == ["sample2", "A002", ""]

    # @pytest.mark.parametrize(
    #     "header_dict,reads_dict,samples_dict,bcl_settings_dict,bcl_data_dict",
    #     [
    #         (
    #             {"IEMFileVersion": "4", "Date": "2024-09-12", "Workflow": "GenerateFASTQ"},
    #             {"Read1Cycles": "151", "Adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
    #             {
    #                 "sample1": {"Sample_ID": "sample1", "sample_name": "test_sample_1", "index": "A001"},
    #                 "sample2": {"Sample_ID": "sample2", "index": "A002", "sample_name": "test_sample_2"},
    #             },
    #             {"SoftwareVersion": "x.y.z", "AdapterBehavior": "trim"},
    #             {
    #                 "sample1": {"Sample_ID": "sample1", "index2": "B001", "index": "A001"},
    #                 "sample2": {"Sample_ID": "sample2", "index": "A002", "index2": "B002"},
    #             },
    #         )
    #     ],
    # )
    # def test_create_bcl_v2_sample_sheet_valid(self, header_dict, reads_dict, samples_dict, bcl_settings_dict, bcl_data_dict):
    #     """
    #     Check that the csv file is created and contains the correct data
    #     """
    #     # Set up
    #     iu = IlluminaUtils()
    #     output_file_name = os.path.join(self.tmp_path, "test_samplesheet")

    #     # Test
    #     iu.create_bcl_v2_sample_sheet(output_file_name, header_dict, reads_dict, samples_dict, bcl_settings_dict, bcl_data_dict)

    #     # Assert
    #     # Check the illumina file
    #     output_illumina_file_csv = output_file_name + "_illumina.csv"
    #     with open(output_illumina_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)
    #         print(content)

    #         # Check the header
    #         assert content[0] == ["[Header]"]
    #         assert ["IEMFileVersion", "4"] in content
    #         assert ["Date", "2024-09-12"] in content
    #         assert ["Workflow", "GenerateFASTQ"] in content

    #         # Check the reads
    #         assert ["[Reads]"] in content
    #         assert ["Read1Cycles", "151"] in content
    #         assert ["Adapter", "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"] in content

    #         # Check the sample data
    #         assert ["[Data]"] in content
    #         assert content[-3] == ["Sample_ID", "index", "sample_name"]
    #         assert content[-2] == ["sample1", "A001", "test_sample_1"]
    #         assert content[-1] == ["sample2", "A002", "test_sample_2"]

    #         # Check the bcl info are not included
    #         assert ["[BCLConvert_Settings]"] not in content
    #         assert ["[BCLConvert_Data]"] not in content

    #     # Check the bcl_convert file
    #     output_bcl_file_csv = output_file_name + "_bclconvert.csv"
    #     with open(output_bcl_file_csv, "r", encoding="ASCII") as f:
    #         reader = csv.reader(f)
    #         content = list(reader)
    #         print(content)

    #         # Check the illumina info is incorporated
    #         assert content[0] == ["[Header]"]
    #         assert ["[Reads]"] in content
    #         assert ["[Data]"] in content

    #         # Check the bcl settings
    #         assert ["[BCLConvert_Settings]"] in content
    #         assert ["SoftwareVersion", "x.y.z"] in content
    #         assert ["AdapterBehavior", "trim"] in content

    # # Check the bcl data
    # assert ["[BCLConvert_Data]"] in content
    # assert content[-3] == ["Sample_ID", "index", "index2"]
    # assert content[-2] == ["sample1", "A001", "B001"]
    # assert content[-1] == ["sample2", "A002", "B002"]

    @pytest.mark.parametrize(
        "header_dict,reads_dict,bcl_settings_dict,bcl_data_dict",
        [
            (
                {"IEMFileVersion": "4", "Date": "2024-09-12", "Workflow": "GenerateFASTQ"},
                {"Read1Cycles": "151", "Adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
                {"SoftwareVersion": "x.y.z", "AdapterBehavior": "trim"},
                {
                    "sample1": {"Sample_ID": "sample1", "index2": "B001", "index": "A001"},
                    "sample2": {"Sample_ID": "sample2", "index": "A002", "index2": "B002"},
                },
            )
        ],
    )
    def test_generate_bcl_samplesheet_valid(self, header_dict, reads_dict, bcl_settings_dict, bcl_data_dict):
        """
        Check that the csv file is created and contains the correct data
        """
        # Set up
        iu = IlluminaUtils()
        output_file_name = os.path.join(self.tmp_path, "test_samplesheet")

        # Test
        iu.generate_bcl_samplesheet(header_dict, reads_dict, bcl_settings_dict, bcl_data_dict, output_file_name)

        # Assert
        output_file = output_file_name + ".csv"
        with open(output_file, "r", encoding="ASCII") as f:
            reader = csv.reader(f)
            content = list(reader)
            print(content)

            # Check the header
            assert content[0] == ["[Header]"]
            assert ["IEMFileVersion", "4"] in content
            assert ["Date", "2024-09-12"] in content
            assert ["Workflow", "GenerateFASTQ"] in content

            # Check the reads
            assert ["[Reads]"] in content
            assert ["Read1Cycles", "151"] in content
            assert ["Adapter", "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"] in content

            # Check the bcl settings
            assert ["[BCLConvert_Settings]"] in content
            assert ["SoftwareVersion", "x.y.z"] in content
            assert ["AdapterBehavior", "trim"] in content

            # Check the bcl data
            assert ["[BCLConvert_Data]"] in content
            assert content[-3] == ["Sample_ID", "index", "index2"]
            assert content[-2] == ["sample1", "A001", "B001"]
            assert content[-1] == ["sample2", "A002", "B002"]

    @pytest.mark.parametrize(
        "header_dict,reads_dict",
        [
            (
                {"IEMFileVersion": "4", "Date": "2024-09-12", "Workflow": "GenerateFASTQ"},
                {"Read1Cycles": "151", "Adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
            )
        ],
    )
    def test_generate_bcl_samplesheet_nobclvalues(self, header_dict, reads_dict):
        """
        Check that the csv file does not contain empty or None BCL dictionary values
        """
        # Set up
        iu = IlluminaUtils()
        output_file_name = os.path.join(self.tmp_path, "test_samplesheet")
        bcl_settings_dict = {}

        # Test
        iu.generate_bcl_samplesheet(header_dict, reads_dict, bcl_settings_dict=bcl_settings_dict, output_file_name=output_file_name)

        # Assert
        output_file = output_file_name + ".csv"
        with open(output_file, "r", encoding="ASCII") as f:
            reader = csv.reader(f)
            content = list(reader)

            # Check the header
            assert content[0] == ["[Header]"]
            assert ["IEMFileVersion", "4"] in content
            assert ["Date", "2024-09-12"] in content
            assert ["Workflow", "GenerateFASTQ"] in content

            # Check the reads
            assert ["[Reads]"] in content
            assert ["Read1Cycles", "151"] in content
            assert ["Adapter", "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"] in content

            # Check BCL info is not included
            assert ["[BCLConvert_Settings]"] not in content
            assert ["[BCLConvert_Data]"] not in content

    # def test_extract_top_unknown_barcode_from_html_nosequence(self):
    # """
    # Pass a file that is html
    # """

    # # Set up
    # iu = IlluminaUtils()
    # html_file = os.path.join(self.tmp_path, "file.html")
    # with open(html_file, "w", encoding="utf-8"):
    #     content = """
    #         <html>
    #         <body>
    #         <h1>Top Unknown Barcodes</h1>
    #         <table>
    #             <tr><th>Sequence</th><th>Count</th></tr>
    #         </table>
    #         </body>
    #         </html>"""
    #     print(content)

    # # Test
    # result = iu.extract_top_unknown_barcode_from_html(html_file)

    # # Assert
    # # assert result is ValueError
    # # self.assertIsInstance(result, ValueError, "Expected a ValueError")
    # with self.assertRaises(ValueError):
    #     iu.extract_top_unknown_barcode_from_html("mock_html_file.html")
