"""
Tests covering the data_transfer module
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

import csv
import logging
import os
from datetime import datetime
from xml.parsers.expat import ExpatError

import pytest
from assertpy import assert_that

from asf_tools.illumina.illumina_utils import (
    atac_reformat_barcode,
    calculate_overridecycle_values,
    count_samples_in_bcl_samplesheet,
    dlp_barcode_data_to_dict,
    extract_cycle_frompath,
    extract_cycle_fromxml,
    extract_illumina_runid_frompath,
    extract_illumina_runid_fromxml,
    extract_matching_item_from_dict,
    filter_readinfo,
    filter_runinfo,
    find_key_recursively,
    generate_bcl_samplesheet,
    generate_bclconfig,
    generate_overridecycle_string,
    group_samples_by_dictkey,
    group_samples_by_index_length,
    index_distance,
    merge_dicts,
    merge_runinfo_dict_fromfile,
    minimum_index_distance,
    reformat_barcode,
    runinfo_xml_to_dict,
    split_by_project_type,
)


class TestIlluminaUtils:
    """Class for parse_runinfo tests"""

    def test_runinfo_xml_to_dict_filenotexist(self):
        # Test and Assert
        assert_that(runinfo_xml_to_dict).raises(FileNotFoundError).when_called_with("file_does_not_exist")

    def test_runinfo_xml_to_dict_isnotxml(self):
        # Test and Assert
        assert_that(runinfo_xml_to_dict).raises(ExpatError).when_called_with("./tests/data/illumina/dummy.txt")

    def test_runinfo_xml_to_dict_isinvalid(self):
        """
        Pass a xml file with compromised content
        """
        # Test and Assert
        assert_that(runinfo_xml_to_dict).raises(ExpatError).when_called_with("./tests/data/illumina/fake_RunInfo.xml")

    def test_find_key_recursively_none(self):
        # Test and Assert
        assert_that(find_key_recursively).raises(TypeError).when_called_with(None)

    def test_find_key_recursively_emptytarget(self):
        # Test and Assert
        assert_that(find_key_recursively).raises(ValueError).when_called_with("./tests/data/illumina/RunInfo.xml", "")

    def test_extract_matching_item_from_dict_returnnone(self):
        """
        Pass empty list to method
        """

        # Set up
        file = "./tests/data/illumina/RunInfo.xml"
        xml_dict = runinfo_xml_to_dict(file)

        # Test and Assert
        assert_that(extract_matching_item_from_dict).raises(TypeError).when_called_with(xml_dict, "info_not_in_file")

    def test_filter_runinfo_machinenotexist(self):
        """
        Tests the `filter_runinfo` method for handling an unrecognized instrument.

        This test method sets up a mock RunInfo dictionary where the instrument
        name does not match any of the predefined patterns in the `filter_runinfo` method.
        The test verifies that the method raises a `ValueError` when it encounters an
        unrecognized instrument.

        The test ensures that `filter_runinfo` properly handles invalid or unknown
        instrument names by raising the appropriate exception.
        """
        # Set up
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
        assert_that(filter_runinfo).raises(ValueError).when_called_with(xml_dict)

    def test_filter_runinfo_isvalid(self):
        # Set up
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

        # Test and Assert
        assert_that(filter_runinfo(xml_dict)).is_equal_to(expected_dict)

    def test_extract_illumina_runid_fromxml(self):
        """
        Pass a valid XML file and test expected RunID values from the dictionary output
        """
        # Set up
        file = "./tests/data/illumina/RunInfo.xml"
        flowcell_runid = "22MKK5LT3"

        # Test and Assert
        assert_that(extract_illumina_runid_fromxml(file)).is_equal_to(flowcell_runid)

    def test_extract_illumina_runid_frompath(self):
        """
        Pass a valid XML file and test expected RunID values from the dictionary output
        """
        # Set up
        path = "./tests/data/illumina/"
        file = "RunInfo.xml"
        flowcell_runid = "22MKK5LT3"

        # Test and Assert
        assert_that(extract_illumina_runid_frompath(path, file)).is_equal_to(flowcell_runid)

    def test_extract_cycle_fromxml_isvalid(self):
        # Set up
        file = "./tests/data/illumina/RunInfo.xml"
        cycle_length = ["151", "10", "10", "151"]

        # Test and Assert
        assert_that(extract_cycle_fromxml(file)).is_equal_to(cycle_length)

    def test_extract_cycle_frompath_isvalid(self):
        # Set up
        path = "./tests/data/illumina/"
        file = "RunInfo.xml"
        cycle_length = ["151", "10", "10", "151"]

        # Test and Assert
        assert_that(extract_cycle_frompath(path, file)).is_equal_to(cycle_length)

    def test_merge_runinfo_dict_fromfile_isvalid(self):
        # Set up
        file = "./tests/data/illumina/RunInfo.xml"

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expected_dict = {
            "run_id": "20240711_LH00442_0033_A22MKK5LT3",
            "end_type": "PE",
            "reads": [
                {"read": "Read 1", "num_cycles": "151"},
                {"read": "Index 2", "num_cycles": "10"},
                {"read": "Index 3", "num_cycles": "10"},
                {"read": "Read 4", "num_cycles": "151"},
            ],
            "current_date": current_datetime,
            "instrument": "LH00442",
            "machine": "NovaSeqX",
            "lane": "8",
        }

        # Test and Assert
        assert_that(merge_runinfo_dict_fromfile(file)).is_equal_to(expected_dict)

    def test_reformat_barcode_isnone(self):
        # Test and Assert
        assert_that(reformat_barcode).raises(TypeError).when_called_with(None)

    def test_reformat_barcode_nobarcode(self):
        """
        Pass a dict without the key "barcode" to method
        """

        # Set up
        test_dict = {"value1": "invalid", "value2": "dictionary"}
        expected = {}

        # Test and Assert
        assert_that(reformat_barcode(test_dict)).is_equal_to(expected)

    def test_reformat_barcode_isvalid(self):
        # Set up
        test_dict = {
            "Sample1": {"barcode": "BC01 (AAGAAAGTTGTCGGTGTG)"},
            "Sample2": {"barcode": "GTTCTT-CTGTGGGGAAT"},
            "Sample3": {"barcode": "15 SI-NA-G2 (ATAACCTA-CGGTGAGC-GATCTTAT-TCCGAGCG)"},
            "Sample4": {"barcode": "GTTCTT"},
        }
        expected_output = {
            "Sample1": {"index": "AAGAAAGTTGTCGGTGTG"},
            "Sample2": {"index": "GTTCTT", "index2": "CTGTGGGGAAT"},
            "Sample3": {"index": "ATAACCTA", "index2": "CGGTGAGC", "index3": "GATCTTAT", "index4": "TCCGAGCG"},
            "Sample4": {"index": "GTTCTT"},
        }

        # Test and Assert
        assert_that(reformat_barcode(test_dict)).is_equal_to(expected_output)

    def test_atac_reformat_barcode_isnone(self):
        # Test and Assert
        assert_that(atac_reformat_barcode).raises(TypeError).when_called_with(None)

    def test_atac_reformat_barcode_nobarcode(self):
        # Set up
        test_dict = {"value1": "invalid", "value2": "dictionary"}
        expected_output = {}

        # Test and Assert
        assert_that(atac_reformat_barcode(test_dict)).is_equal_to(expected_output)

    def test_atac_reformat_barcode_isvalid(self):
        # Set up
        test_dict = {
            "Sample1": {"barcode": "BC01 (AAGAAAGTTGTCGGTGTG)"},
            "Sample2": {"barcode": "GTTCTT-CTGTGGGGAAT-ATTCTT-CTGTGAAT"},
            "Sample3": {"barcode": "15 SI-NA-G2 (ATAACCTA-CGGTGAGC-GATCTTAT-TCCGAGCG)"},
        }
        expected_output = {
            "Sample1": {"index": ["AAGAAAGTTGTCGGTGTG"]},
            "Sample2": {"index": ["GTTCTT", "CTGTGGGGAAT", "ATTCTT", "CTGTGAAT"]},
            "Sample3": {"index": ["ATAACCTA", "CGGTGAGC", "GATCTTAT", "TCCGAGCG"]},
        }

        # Test and Assert
        assert_that(atac_reformat_barcode(test_dict)).is_equal_to(expected_output)

    def test_group_samples_by_index_length_isnone(self):
        # Test and Assert
        assert_that(group_samples_by_index_length).raises(TypeError).when_called_with(None)

    def test_group_samples_by_index_length_isnotadict(self):
        # Test and Assert
        assert_that(group_samples_by_index_length).raises(TypeError).when_called_with("not_a_dict")

    def test_group_samples_by_index_length_isvalid(self):
        # Set up
        test_dict = {
            "Sample1": {"index": "AAGATAGTGA"},
            "Sample2": {"index": "GTTCTT", "index2": "CTGTGGGAAT"},
            "Sample3": {"index": "ATTATT", "index2": "ATGTGGCCTT"},
        }
        expected_output = [{"index_length": (10, 0), "samples": ["Sample1"]}, {"index_length": (6, 10), "samples": ["Sample2", "Sample3"]}]

        # Test and Assert
        assert_that(group_samples_by_index_length(test_dict)).is_equal_to(expected_output)

    def test_group_samples_by_dictkey_isnone(self):
        # Test and Assert
        assert_that(group_samples_by_dictkey).raises(TypeError).when_called_with(None)

    def test_group_samples_by_dictkey_isinvalid(self):
        # Test and Assert
        assert_that(group_samples_by_dictkey).raises(ValueError).when_called_with(["list", "not", "dictionary"], "key")

    def test_group_samples_by_dictkey_missingkey(self):
        # Set up
        valid_dict = {"sample": {"key1": "value1", "key2": "value2"}}
        expected_output = {}

        # Test and Assert
        assert_that(group_samples_by_dictkey(valid_dict, "missing_key")).is_equal_to(expected_output)

    def test_group_samples_by_dictkey_isvalid(self):
        # Set up
        valid_dict1 = {"sample": {"key1": "matching_value"}, "sample2": {"key1": "matching_value"}, "sample3": {"key1": "different_value"}}
        valid_dict2 = {
            "sample3": {"key1": "value", "key2": "matching_value"},
            "sample4": {"key1": "value", "key2": "matching_value"},
            "sample5": {"different_key": "value"},
        }
        expected_output1 = {"matching_value": ["sample", "sample2"], "different_value": ["sample3"]}
        expected_output2 = {"matching_value": ["sample3", "sample4"]}

        # Test and Assert
        assert_that(group_samples_by_dictkey(valid_dict1, "key1")).is_equal_to(expected_output1)
        assert_that(group_samples_by_dictkey(valid_dict2, "key2")).is_equal_to(expected_output2)

    def test_split_by_project_type_sample_isnone(self):
        # Set up
        sample_info = {"sample_1": {None}, "sample_2": None, "sample_3": {"invalid_value"}}
        constants_dict = {"constant_1": ["value_1"]}
        expected_output = {"constant_1": {}, "all_samples": {}}

        # Test
        results = split_by_project_type(sample_info, constants_dict)

        # Assert
        assert_that(results).is_equal_to(expected_output)

    def test_split_by_project_type_category_isnone(self):
        # Set up
        sample_info = {"sample_2": {"project_type": "value_2", "lanes": "1", "barcode": "OB (ATAA-GGTC)"}}
        constants_dict = {"constant_1": None}
        expected_output = {
            "constant_1": {},
            "other_samples": {
                "sample_2_lane_1": {"Lane": "1", "Sample_ID": "sample_2", "index": "ATAA", "index2": "GGTC"},
            },
            "all_samples": {"sample_2_lane_1": {"Lane": "1", "Sample_ID": "sample_2", "index": "ATAA", "index2": "GGTC"}},
        }

        # Test and Assert
        assert_that(split_by_project_type(sample_info, constants_dict)).is_equal_to(expected_output)

    def test_split_by_project_type_isinvalid(self):
        # Set up
        sample_info = ["not_a_dict"]
        constants_dict = {"constant_1": "value_1"}

        sample_info_2 = {
            "sample_2": "value_2",
        }
        constants_dict_2 = "not_a_dict"

        # Test and Assert
        assert_that(split_by_project_type).raises(ValueError).when_called_with(sample_info, constants_dict)
        assert_that(split_by_project_type).raises(ValueError).when_called_with(sample_info_2, constants_dict_2)

    def test_split_by_project_type_nomatch(self):
        """
        Pass a dict without a "project_type" nor "data_analysis_type" value to method
        """

        # Set up
        sample_info = {
            "sample_1": {"no_project_type": "none", "lanes": "1", "barcode": "BC (ATCG)"},
        }
        constants_dict = {"constant_1": ["value_1"]}
        expected_output = {"constant_1": {}, "all_samples": {"sample_1_lane_1": {"Sample_ID": "sample_1", "Lane": "1", "index": "ATCG"}}}

        # Test and Assert
        assert_that(split_by_project_type(sample_info, constants_dict)).is_equal_to(expected_output)

    def test_split_by_project_type_isvalid(self):
        # Set up
        sample_info = {
            "sample_1": {"project_type": "value_1", "lanes": "1", "barcode": "BC (ATCG)"},
            "sample_2": {"project_type": "value_2", "lanes": ["1", "2"], "barcode": "OB (ATAA-GGTC)"},
            "sample_3": {"data_analysis_type": "other_value_2", "lanes": "3", "barcode": "AAAT-ATGC"},
            "sample_4": {"project_type": "value_4", "lanes": "4", "barcode": "CGTA"},
            "sample_5": {"project_type": "value_5", "lanes": "5", "barcode": "GCCA-CCCG"},
        }
        constants_dict = {"constant_1": ["value_1", "other_value_1"], "CONSTANT_2": ["value_2", "other_value_2"]}
        expected_output = {
            "constant_1": {"sample_1_lane_1": {"Lane": "1", "Sample_ID": "sample_1", "index": "ATCG"}},
            "constant_2": {
                "sample_2_lane_1": {"Lane": "1", "Sample_ID": "sample_2", "index": "ATAA", "index2": "GGTC"},
                "sample_2_lane_2": {"Lane": "2", "Sample_ID": "sample_2", "index": "ATAA", "index2": "GGTC"},
                "sample_3_lane_3": {"Lane": "3", "Sample_ID": "sample_3", "index": "AAAT", "index2": "ATGC"},
            },
            "other_samples": {
                "sample_4_lane_4": {"Lane": "4", "Sample_ID": "sample_4", "index": "CGTA"},
                "sample_5_lane_5": {"Lane": "5", "Sample_ID": "sample_5", "index": "GCCA", "index2": "CCCG"},
            },
            "all_samples": {
                "sample_1_lane_1": {"Lane": "1", "Sample_ID": "sample_1", "index": "ATCG"},
                "sample_2_lane_1": {"Lane": "1", "Sample_ID": "sample_2", "index": "ATAA", "index2": "GGTC"},
                "sample_2_lane_2": {"Lane": "2", "Sample_ID": "sample_2", "index": "ATAA", "index2": "GGTC"},
                "sample_3_lane_3": {"Lane": "3", "Sample_ID": "sample_3", "index": "AAAT", "index2": "ATGC"},
                "sample_4_lane_4": {"Lane": "4", "Sample_ID": "sample_4", "index": "CGTA"},
                "sample_5_lane_5": {"Lane": "5", "Sample_ID": "sample_5", "index": "GCCA", "index2": "CCCG"},
            },
        }

        # Test and Assert
        assert_that(split_by_project_type(sample_info, constants_dict)).is_equal_to(expected_output)

    def test_calculate_overridecycle_values_indexnone(self):
        # Test and Assert
        assert_that(calculate_overridecycle_values).raises(TypeError).when_called_with("", 10, 8)
        assert_that(calculate_overridecycle_values).raises(TypeError).when_called_with(None, 10, 8)

    def test_calculate_overridecycle_values_integernone(self):
        # Test and Assert
        assert_that(calculate_overridecycle_values).raises(TypeError).when_called_with("Value", None, 8)
        assert_that(calculate_overridecycle_values).raises(TypeError).when_called_with("Value", 10, None)
        assert_that(calculate_overridecycle_values).raises(TypeError).when_called_with("Value", 10)

    def test_calculate_overridecycle_values_negativeinteger(self):
        # Test and Assert
        assert_that(calculate_overridecycle_values).raises(TypeError).when_called_with("Value", 10, -8)
        assert_that(calculate_overridecycle_values).raises(TypeError).when_called_with("Value", -10, 8)

    def test_calculate_overridecycle_values_negativedifference(self):
        # Test and Assert
        assert_that(calculate_overridecycle_values).raises(ValueError).when_called_with("Value", 1, 8)

    def test_generate_overridecycle_string_dualindex_isvalid(self):
        # Set up
        expected = "Y151;I8N2;I8N2;Y151"

        # Test and Assert
        assert_that(generate_overridecycle_string("AATTCCGG", 10, 151, "ttaaggcc", 10, 151)).is_equal_to(expected)

    def test_generate_overridecycle_string_dualindex_nozerovalues(self):
        """
        Pass indexes with different lengths to method
        """

        # Set up
        expected_1 = "Y151;I8N2;I10;Y151"
        expected_2 = "Y151;I10;I8N2;Y151"

        # Test and Assert
        assert_that(generate_overridecycle_string("AATTCCGG", 10, 151, "ttaaggcctg", 10, 151)).is_equal_to(expected_1)
        assert_that(generate_overridecycle_string("AATTCCGGAT", 10, 151, "ttaaggcc", 10, 151)).is_equal_to(expected_2)

    def test_generate_overridecycle_string_singleindex_isvalid(self):
        # Set up
        expected = "N10Y151;I8;N10Y151"

        # Test and Assert
        assert_that(generate_overridecycle_string("AATTCCGG", 10, 151)).is_equal_to(expected)

    def test_index_distance_isvalid(self):
        # Test and Assert
        seq1 = "AGCT"
        seq2 = "AGCT"
        assert_that(index_distance(seq1, seq2)).is_equal_to(0)

        seq3 = "AGCT"
        seq4 = "TCGA"
        assert_that(index_distance(seq3, seq4)).is_equal_to(4)

        seq5 = "AGCT"
        seq6 = "TGCT"
        assert_that(index_distance(seq5, seq6)).is_equal_to(1)

    def test_minimum_index_distance_isvalid(self):
        # Test and Assert
        sequences = ["AGCT", "AGCT", "AGCT"]
        assert_that(minimum_index_distance(sequences)).is_equal_to(0)

        sequences = ["AGCT", "TGCA"]
        assert_that(minimum_index_distance(sequences)).is_equal_to(2)

        sequences = ["AGGT", "TGCA", "AGCC"]
        assert_that(minimum_index_distance(sequences)).is_equal_to(2)

    def test_dlp_barcode_data_to_dict_filenotexists(self):
        # Test and Assert
        assert_that(dlp_barcode_data_to_dict).raises(FileNotFoundError).when_called_with("file_does_not_exist", None)

    def test_dlp_barcode_data_to_dict_isvalid(self):
        # Set up
        file_path = "./tests/data/illumina/dlp_barcode_extended_info_testdataset.csv"
        expected = {
            "General_sample_name_i7_313-i5_313": {
                "Lane": "01x_01y",
                "index": "CAACCTAG",
                "index2": "AGGTCTGT",
                "Sample_ID": "General_sample_name_i7_313-i5_313",
            },
            "General_sample_name_i7_314-i5_313": {
                "Lane": "01x_02y",
                "index": "AAGGACAC",
                "index2": "AGGTCTGT",
                "Sample_ID": "General_sample_name_i7_314-i5_313",
            },
            "General_sample_name_i7_315-i5_313": {
                "Lane": "01x_03y",
                "index": "TGCAGGTA",
                "index2": "AGGTCTGT",
                "Sample_ID": "General_sample_name_i7_315-i5_313",
            },
            "General_sample_name_i7_313-i5_314": {
                "Lane": "02x_01y",
                "index": "CAACCTAG",
                "index2": "CCACAACA",
                "Sample_ID": "General_sample_name_i7_313-i5_314",
            },
            "General_sample_name_i7_314-i5_314": {
                "Lane": "02x_02y",
                "index": "AAGGACAC",
                "index2": "CCACAACA",
                "Sample_ID": "General_sample_name_i7_314-i5_314",
            },
            "General_sample_name_i7_315-i5_314": {
                "Lane": "02x_03y",
                "index": "TGCAGGTA",
                "index2": "CCACAACA",
                "Sample_ID": "General_sample_name_i7_315-i5_314",
            },
        }

        # Test and Assert
        assert_that(dlp_barcode_data_to_dict(file_path, "General_sample_name")).is_equal_to(expected)

    def test_generate_bclconfig_invalidmachine(self):
        # Set up
        fake_list = []

        # Test and Assert
        assert_that(generate_bclconfig).raises(ValueError).when_called_with(fake_list, "flowcell")

    def test_generate_bclconfig_invalidflowcell(self):
        # Test and Assert
        assert_that(generate_bclconfig).raises(ValueError).when_called_with("machine", 123)

    def test_generate_bclconfig_isvalid(self):
        """
        Test with only required parameters, no extra fields
        """
        # Set up
        expected = {
            "Header": {"FileFormatVersion": 2, "InstrumentPlatform": "NovaseqX", "RunName": "Flowcell123"},
            "BCLConvert_Settings": {"SoftwareVersion": "4.2.7", "FastqCompressionFormat": "gzip"},
        }

        # Test and Assert
        assert_that(generate_bclconfig("NovaseqX", "Flowcell123")).is_equal_to(expected)

    def test_generate_bclconfig_override_and_additional_fields(self):
        """
        # Test with both overrides and additional fields
        """
        # Set up
        header_extra = {"FileFormatVersion": 3, "ExtraHeaderField": "TestHeaderValue"}
        bclconvert_extra = {"SoftwareVersion": "4.3.0", "ExtraBCLConvertField": "TestBCLValue"}
        expected = {
            "Header": {"FileFormatVersion": 3, "InstrumentPlatform": "NovaseqX", "RunName": "Flowcell123", "ExtraHeaderField": "TestHeaderValue"},
            "BCLConvert_Settings": {"SoftwareVersion": "4.3.0", "FastqCompressionFormat": "gzip", "ExtraBCLConvertField": "TestBCLValue"},
        }

        # Test and Assert
        assert_that(
            generate_bclconfig("NovaseqX", "Flowcell123", header_parameters=header_extra, bclconvert_parameters=bclconvert_extra)
        ).is_equal_to(expected)

    def test_count_samples_in_bcl_samplesheet_isinvalid(self):
        # Set up
        invalid_entry = []
        invalid_entry2 = 2

        # Test and Assert
        assert_that(count_samples_in_bcl_samplesheet).raises(ValueError).when_called_with("./", invalid_entry)
        assert_that(count_samples_in_bcl_samplesheet).raises(ValueError).when_called_with("./", invalid_entry2)

    def test_count_samples_in_bcl_samplesheet_nofileinput(self):
        # Set up
        invalid_path = "file_does_not_exist"

        # Test and Assert
        assert_that(count_samples_in_bcl_samplesheet).raises(FileNotFoundError).when_called_with(invalid_path, "string")

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
        # Test and Assert
        assert_that(runinfo_xml_to_dict(file)).is_equal_to(expected_dict)

    @pytest.mark.parametrize(
        "dic,expected_list",
        [
            ({"run": {"@Id": "20240711_LH00442_0033_A22MKK5LT3"}}, ["20240711_LH00442_0033_A22MKK5LT3"]),
            ({"run": {"other_info": {"@Id": "20240711_LH00442_0033_A22MKK5LT3"}}}, ["20240711_LH00442_0033_A22MKK5LT3"]),
        ],
    )
    def test_find_key_recursively_isvalid(self, dic, expected_list):
        # Test and Assert
        assert_that(find_key_recursively(dic, "@Id")).is_equal_to(expected_list)

    @pytest.mark.parametrize(
        "list_info,expected_output", [({"run": {"@Id": "20240711_LH00442_0033_A22MKK5LT3"}}, "20240711_LH00442_0033_A22MKK5LT3")]
    )
    def test_extract_matching_item_from_dict_isvalid(self, list_info, expected_output):
        # Test and Assert
        assert_that(extract_matching_item_from_dict(list_info, "@Id")).is_equal_to(expected_output)

    @pytest.mark.parametrize(
        "file,expected_dict",
        [
            (
                "./tests/data/illumina/RunInfo.xml",
                {
                    "run_id": "20240711_LH00442_0033_A22MKK5LT3",
                    "end_type": "PE",
                    "reads": [
                        {"read": "Read 1", "num_cycles": "151"},
                        {"read": "Index 2", "num_cycles": "10"},
                        {"read": "Index 3", "num_cycles": "10"},
                        {"read": "Read 4", "num_cycles": "151"},
                    ],
                },
            )
        ],
    )
    def test_filter_readinfo_isvalid(self, file, expected_dict):
        # Test
        xml_info = runinfo_xml_to_dict(file)
        read_info = filter_readinfo(xml_info)

        # Assert
        assert_that(read_info).is_equal_to(expected_dict)

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
        # Test and Assert
        assert_that(merge_dicts(dict1, dict2, "run_id")).is_equal_to(expected_merged_dict)

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
    def test_generate_bcl_samplesheet_valid(self, header_dict, reads_dict, bcl_settings_dict, bcl_data_dict, tmp_path):
        """
        Check that the csv file is created and contains the correct data
        """
        # Set up
        output_file_path = os.path.join(tmp_path, "test_samplesheet.csv")

        # Test
        generate_bcl_samplesheet(header_dict, reads_dict, bcl_settings_dict, bcl_data_dict, output_file_path)

        # Assert
        output_file = output_file_path
        with open(output_file, "r", encoding="ASCII") as f:
            reader = csv.reader(f)
            content = list(reader)
            print(content)

            # Check the header
            assert content[0] == ["[Header]", "", "", ""]
            assert ["IEMFileVersion", "4", "", ""] in content
            assert ["Date", "2024-09-12", "", ""] in content
            assert ["Workflow", "GenerateFASTQ", "", ""] in content

            # Check the reads
            assert ["[Reads]", "", "", ""] in content
            assert ["Read1Cycles", "151", "", ""] in content
            assert ["Adapter", "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA", "", ""] in content

            # Check the bcl settings
            assert ["[BCLConvert_Settings]", "", "", ""] in content
            assert ["SoftwareVersion", "x.y.z", "", ""] in content
            assert ["AdapterBehavior", "trim", "", ""] in content

            # Check the bcl data
            assert ["[BCLConvert_Data]", "", "", ""] in content
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
    def test_generate_bcl_samplesheet_nobclvalues(self, header_dict, reads_dict, tmp_path):
        """
        Check that the csv file does not contain empty or None BCL dictionary values
        """
        # Set up
        output_file_path = os.path.join(tmp_path, "test_samplesheet.csv")
        bcl_settings_dict = {}

        # Test
        generate_bcl_samplesheet(header_dict, reads_dict, bcl_settings_dict=bcl_settings_dict, output_file_path=output_file_path)

        # Assert
        output_file = output_file_path
        with open(output_file, "r", encoding="ASCII") as f:
            reader = csv.reader(f)
            content = list(reader)

            # Check the header
            assert content[0] == ["[Header]", "", "", ""]
            assert ["IEMFileVersion", "4", "", ""] in content
            assert ["Date", "2024-09-12", "", ""] in content
            assert ["Workflow", "GenerateFASTQ", "", ""] in content

            # Check the reads
            assert ["[Reads]", "", "", ""] in content
            assert ["Read1Cycles", "151", "", ""] in content
            assert ["Adapter", "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA", "", ""] in content

            # Check BCL info is not included
            assert ["[BCLConvert_Settings]"] not in content
            assert ["[BCLConvert_Data]"] not in content

    def test_count_samples_in_bcl_samplesheet_isnone(self, tmp_path):
        """
        Pass input string not present in file content
        """
        # Set up
        file_path = os.path.join(tmp_path, "test_bcl_samplesheet.csv")
        with open(file_path, "w", encoding="ASCII") as f:
            f.write("[Header],,\n")
            f.write("[FileFormatVersion],2,\n")
        expected = None

        # Test and Assert
        assert_that(count_samples_in_bcl_samplesheet(file_path, "Sample_ID")).is_equal_to(expected)

    def test_count_samples_in_bcl_samplesheet_isvalid(self, tmp_path):
        # Set up
        # Create file with content
        file_path = os.path.join(tmp_path, "test_bcl_samplesheet.csv")
        with open(file_path, "w", encoding="ASCII") as f:
            f.write("[Header],,\n")
            f.write("[FileFormatVersion],2,\n")
            f.write("[BCLConvert_Data],,\n")
            f.write("Lane,Sample_ID,index,index2\n")
            f.write("1,WAR6617A1,CGAATTGC,GTAAGGTG\n")
            f.write("2,WAR6617A1,CGAATTGC,GTAAGGTG\n")
        expected = 2

        file_path2 = os.path.join(tmp_path, "test_bcl_samplesheet_2.csv")
        with open(file_path2, "w", encoding="ASCII") as f:
            f.write("[Header],,\n")
            f.write("Lane,Sample_ID,index,index2\n")
            f.write("1,WAR6617A1,CGAATTGC,GTAAGGTG\n")
            f.write("2,WAR6617A1,CGAATTGC,GTAAGGTG\n")
            f.write("2,WAR6617A1,CGAATTGC,GTAAGGTG\n")
        expected2 = 3

        # Test and Assert
        assert_that(count_samples_in_bcl_samplesheet(file_path, "Sample_ID")).is_equal_to(expected)
        assert_that(count_samples_in_bcl_samplesheet(file_path2, "Sample_ID")).is_equal_to(expected2)
