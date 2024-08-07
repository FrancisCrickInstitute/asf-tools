"""
Tests covering the data_transfer module
"""

import unittest

from asf_tools.illumina.illumina_utils import IlluminaUtils

class TestRunInfoParse(unittest.TestCase):
    """Class for parse_runinfo tests"""
# runinfo_xml_to_dict - need to test for: none, empty file, something other than file as an input
# filter_runinfo - need to test for: the presence of runid,instrument info, machine that isn't in the mapping dict
# filter_readinfo - need to test for: the presence of runid and reads

    def test_runinfo_xml_to_dict_isnone(self):
        # Set up
        iu = IlluminaUtils()
        file = "./tests/data/illumina/RunInfo.xml"

        # Test
        xml_info = iu.runinfo_xml_to_dict(file)
        # print(xml_info)

        # Assert
        assert xml_info == []

    def test_runinfo_xml_to_dict_isvalid(self):
        # Set up
        iu = IlluminaUtils()
        file = "./tests/data/illumina/RunInfo.xml"

        # Test
        xml_info = iu.runinfo_xml_to_dict(file)
        # print(xml_info)

        # Assert
        assert xml_info == []

    # def test_runinfo_parser(self):
    #     # Set up
    #     iu = IlluminaUtils()
    #     file = "./tests/data/illumina/RunInfo.xml"

    #     # Test
    #     xml_info = iu.runinfo_parser(file)
    #     # print(xml_info)

    #     # Assert
    #     assert xml_info == []

    def test_filter_readinfo(self):
        # Set up
        iu = IlluminaUtils()
        file = "./tests/data/illumina/RunInfo.xml"

        # Test
        xml_info = iu.runinfo_xml_to_dict(file)
        read_info = iu.filter_readinfo(xml_info)
        # print(xml_info)

        # Assert
        assert read_info == []

    def test_merge_runinfo_dict_fromfile(self):
        # Set up
        iu = IlluminaUtils()
        file = "./tests/data/illumina/RunInfo.xml"

        # Test
        filtered_info = iu.merge_runinfo_dict_fromfile(file)
        # print(filtered_info)

        # Assert
        assert filtered_info == []