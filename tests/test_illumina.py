"""
Tests covering the data_transfer module
"""

import unittest

from asf_tools.illumina.illumina_utils import IlluminaUtils

class TestRunInfoParse(unittest.TestCase):
    """Class for parse_runinfo tests"""
    
    def test_runinfo_parser(self):
        # Set up
        iu = IlluminaUtils()
        file = "./tests/data/illumina/RunInfo.xml"

        # Test
        xml_info = iu.runinfo_parser(file)
        print(xml_info)
        assert xml_info == []