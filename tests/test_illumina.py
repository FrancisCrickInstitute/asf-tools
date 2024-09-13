"""
Tests covering the data_transfer module
"""

import os
import unittest
from datetime import datetime
from xml.parsers.expat import ExpatError

import pytest

from asf_tools.illumina.illumina_utils import IlluminaUtils

from .utils import with_temporary_folder


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
        }

        # Test
        filtered_info = iu.merge_runinfo_dict_fromfile(file)
        # print(filtered_info)

        # Assert
        assert filtered_info == expected_dict


class TestIlluminaUtilsWithFixtures:
    """Class for IlluminaUtils tests with fixtures"""

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

    @pytest.mark.parametrize(
        "header_dict,settings_dict,samples_dict",
        [
            (
                {"IEMFileVersion": "4", "Date": "2024-09-12", "Workflow": "GenerateFASTQ"},
                {"Read1Cycles": "151", "Adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
                {
                    "sample1": {"sample_ID": "sample1", "sample_name": "test_sample_1", "index": "A001"},
                    "sample2": {"sample_ID": "sample2", "sample_name": "test_sample_2", "index": "A002"},
                },
            )
        ],
    )
    def test_dict_to_basic_samplesheet_valid(self, header_dict, settings_dict, samples_dict, tmp_path):
        """
        Check that the csv file is created and contains the correct data
        """
        # Set up
        iu = IlluminaUtils()
        output_file_name = os.path.join(tmp_path, "test_samplesheet.csv")

        # Test
        iu.dict_to_basic_samplesheet(header_dict, settings_dict, samples_dict, output_file_name)

        # Assert
        assert os.path.exists(output_file_name)

        with open(output_file_name, "r", encoding="UTF-8") as f:
            content = f.read()

            # Check header content
            assert "[Header]" in content
            assert "IEMFileVersion,4" in content
            assert "Date,2024-09-12" in content
            assert "Workflow,GenerateFASTQ" in content

            # Check settings content
            assert "[Settings]" in content
            assert "Read1Cycles,151" in content
            assert "Adapter,AGATCGGAAGAGCACACGTCTGAACTCCAGTCA" in content

            # Check sample data
            assert "[Data]" in content
            assert "sample_ID,sample_name,index" in content
            assert "sample1,test_sample_1,A001" in content
            assert "sample2,test_sample_2,A002" in content

    @pytest.mark.parametrize(
            "header_dict,settings_dict",
            [
                (
                    {"IEMFileVersion": "4", "Date": "2024-09-12", "Workflow": "GenerateFASTQ"},
                    {"Read1Cycles": "151", "Adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
                )
            ],
        )
    def test_dict_to_basic_samplesheet_no_samples(self, tmp_path, header_dict, settings_dict):
        """
        Test behavior with an empty samples_dict
        """
        # Set up
        iu = IlluminaUtils()
        empty_samples_dict = {}
        output_file_name = os.path.join(tmp_path, "test_samplesheet.csv")

        # Test
        iu.dict_to_basic_samplesheet(header_dict, settings_dict, empty_samples_dict, output_file_name)

        # Assert
        with open(output_file_name, "r", encoding="UTF-8") as f:
            content = f.read()

            # Ensure the header and settings sections are present
            assert "[Header]" in content
            assert "[Settings]" in content
            # Ensure that [Data] section is present but empty
            assert "[Data]" in content
            assert "sample_ID" not in content

    @pytest.mark.parametrize(
            "header_dict,settings_dict",
            [
                (
                    {"IEMFileVersion": "4", "Date": "2024-09-12", "Workflow": "GenerateFASTQ"},
                    {"Read1Cycles": "151", "Adapter": "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"},
                )
            ],
        )
    def test_dict_to_basic_samplesheet_partial_sample_info(self, tmp_path, header_dict, settings_dict):
        """
        Test with samples missing some fields
        """
        # Set up
        iu = IlluminaUtils()

        incomplete_samples_dict = {
            "sample1": {"sample_ID": "sample1", "index": "A001"},  # missing sample_name
            "sample2": {"sample_ID": "sample2", "sample_name": "test_sample_2"},  # missing index
        }
        output_file_name = os.path.join(tmp_path, "test_samplesheet.csv")

        # Test
        iu.dict_to_basic_samplesheet(header_dict, settings_dict, incomplete_samples_dict, output_file_name)

        # Assert
        with open(output_file_name, "r", encoding="UTF-8") as f:
            content = f.read()

            # Ensure the missing fields are replaced with empty strings
            assert "[Data]" in content
            assert "sample_ID,sample_name,index" in content
            assert "sample1,,A001" in content # missing sample_name is empty
            assert "sample2,test_sample_2," in content # missing index is empty
