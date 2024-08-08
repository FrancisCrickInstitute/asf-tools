"""
Tests covering the data_transfer module
"""

import unittest
from xml.parsers.expat import ExpatError

import pytest

from asf_tools.illumina.illumina_utils import IlluminaUtils


class TestRunInfoParse(unittest.TestCase):
    """Class for parse_runinfo tests"""

    # filter_runinfo - need to test for: machine that isn't in the mapping dict
    # add test for find_key_recursively and extract_matching_item_from_xmldict

    def test_runinfo_xml_to_dict_isnone(self):
        """
        Pass None to method
        """

        # Set up
        iu = IlluminaUtils()

        # Test and Assert
        with self.assertRaises(TypeError):
            iu.runinfo_xml_to_dict(None)

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

    def test_filter_runinfo_isnone(self):
        """
        Pass None to method
        """

        # Set up
        iu = IlluminaUtils()

        # Test and Assert
        with self.assertRaises(TypeError):
            iu.filter_runinfo(None)

    def test_merge_runinfo_dict_fromfile(self):
        # Set up
        iu = IlluminaUtils()
        file = "./tests/data/illumina/RunInfo.xml"

        # Test
        filtered_info = iu.merge_runinfo_dict_fromfile(file)
        # print(filtered_info)

        # Assert
        assert filtered_info == []


class TestRunInfoParseWithFixtures:
    """Class for parse_runinfo tests with fixtures"""

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
        Pass a valid XML file
        """

        # Set up
        iu = IlluminaUtils()

        # Test
        xml_info = iu.runinfo_xml_to_dict(file)
        print(xml_info)

        # Assert
        assert xml_info == expected_dict

    @pytest.mark.parametrize("file,expected_dict", [("./tests/data/illumina/RunInfo.xml", {})])
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
        "input_dict,expected_dict",
        [
            (
                {
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
                },
                "empty",
            )
        ],
    )
    def test_filter_runinfo_isinvalid(self, input_dict, expected_dict):
        # Set up
        iu = IlluminaUtils()

        # Test
        run_info = iu.filter_runinfo(input_dict)
        # print(xml_info)

        # Assert
        assert run_info == expected_dict
        # with self.assertRaises(ExpatError):
        #     iu.filter_runinfo(xml_info)
