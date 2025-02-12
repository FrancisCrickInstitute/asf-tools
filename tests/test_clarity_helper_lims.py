"""
Clarity helper API Tests
"""

import os
import unittest
import warnings
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import ConnectionError, HTTPError  # pylint: disable=redefined-builtin

from asf_tools.api.clarity.models import Stub

from .mocks.clarity_helper_lims_mock import ClarityHelperLimsMock


API_TEST_DATA = "tests/data/api/clarity"


class TestClarityHelperLims(unittest.TestCase):
    """Class for testing the clarity api wrapper"""

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

    def test_clarity_helper_get_artifacts_from_runid_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_artifacts_from_runid(None)

    def test_clarity_helper_get_artifacts_from_runid_isinvalid(self):
        """
        Pass runid that does not exist
        """

        # Setup
        runid = "fake_runid"

        # Test and Assert
        with self.assertRaises(KeyError):
            self.api.get_artifacts_from_runid(runid)

    def test_clarity_helper_get_lane_from_runid_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_lane_from_runid(None)

    def test_clarity_helper_get_lane_from_runid_isinvalid(self):
        """
        Pass an invalid run_id to method
        """

        # Test and Assert
        with self.assertRaises(KeyError):
            self.api.get_lane_from_runid("Fake_runid")

    def test_clarity_helper_get_samples_from_artifacts_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_samples_from_artifacts(None)

    def test_clarity_helper_get_samples_from_artifacts_isinvalid(self):
        """
        Pass an artifact that does not exist
        """

        # Setup
        artifacts_list = [Stub(id="TestID", uri="https://asf-claritylims.thecrick.org/api/v2/artifacts/TEST", name=None, limsid="TestID")]

        # Test and Assert
        with self.assertRaises((HTTPError, ConnectionError)):
            self.api.get_samples_from_artifacts(artifacts_list)

    def test_clarity_helper_get_sample_info_isnone(self):
        """
        Pass None to method
        """

        # Test
        results = self.api.get_sample_info(None)

        # Assert
        assert results is None

    def test_clarity_helper_get_barcode_from_reagenttypes_isnone(self):
        """
        Pass None to method
        """

        # Test
        results = self.api.get_barcode_from_reagenttypes(None)

        # Assert
        assert results is None

    def test_clarity_helper_get_barcode_from_reagenttypes_isinvalid(self):
        """
        Pass a valid input to method
        """
        # Setup
        barcode = "fake_barcode"

        # Test and Assert
        with warnings.catch_warnings(record=True) as warn:
            warnings.simplefilter("always")  # Catch all warnings

            results = self.api.get_barcode_from_reagenttypes(barcode)  # Call the function that raises a warning

            # Assert
            # check the barcode returned and if a warning was raised
            self.assertEqual(results, barcode)
            self.assertEqual(len(warn), 1)
            self.assertIs(warn[-1].category, UserWarning)

    @patch("asf_tools.api.clarity.clarity_lims.xmltodict.parse")
    @patch.object(ClarityHelperLimsMock, "get_with_uri")
    def test_clarity_helper_get_barcode_from_reagenttypes_warning_1(self, mock_get_with_uri, mock_xmltodict_parse):
        """
        Mock api connection to return the first warning
        """
        # Setup
        barcode = "fake_barcode"

        mock_get_with_uri.return_value = "<xml>mock_reagent_types</xml>"
        mock_xmltodict_parse.return_value = {}

        # Test
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            results = self.api.get_barcode_from_reagenttypes(barcode)

            # Assert
            # check the barcode returned and if the correct warning was raised
            self.assertEqual(results, barcode)
            self.assertTrue(any(issubclass(warning.category, UserWarning) for warning in w))
            self.assertTrue(any("Missing 'rtp:reagent-types'" in str(warning.message) for warning in w))

    @patch("asf_tools.api.clarity.clarity_lims.xmltodict.parse")
    @patch.object(ClarityHelperLimsMock, "get_with_uri")
    def test_clarity_helper_get_barcode_from_reagenttypes_warning_2(self, mock_get_with_uri, mock_xmltodict_parse):
        """
        Mock api connection to return the second warning
        """
        # Setup
        barcode = "fake_barcode"

        mock_get_with_uri.return_value = "<xml>mock_reagent_types</xml>"
        mock_xmltodict_parse.return_value = {"rtp:reagent-types": {"reagent-type": {}}}

        # Test
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            results = self.api.get_barcode_from_reagenttypes(barcode)

            # Assert
            # check the barcode returned and if the correct warning was raised
            self.assertEqual(results, barcode)
            self.assertTrue(any(issubclass(warning.category, UserWarning) for warning in w))
            self.assertTrue(any("Missing 'reagent-type' or 'uri'" in str(warning.message) for warning in w))

    @patch("asf_tools.api.clarity.clarity_lims.xmltodict.parse")
    @patch.object(ClarityHelperLimsMock, "get_with_uri")
    def test_clarity_helper_get_barcode_from_reagenttypes_warning_3(self, mock_get_with_uri, mock_xmltodict_parse):
        """
        Mock api connection to return the third warning
        """
        # Setup
        barcode = "fake_barcode"

        mock_get_with_uri.side_effect = [
            "<xml>mock_reagent_types</xml>",  # first API call
            "<xml>mock_reagent_type_details</xml>",  # second API call
        ]

        mock_xmltodict_parse.side_effect = [
            {"rtp:reagent-types": {"reagent-type": {"uri": "mock_uri"}}},  # first parsed XML
            {"rtp:reagent-type": {"special-type": {"attribute": {"name": "InvalidName"}}}},  # second parsed XML
        ]

        # Test
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            results = self.api.get_barcode_from_reagenttypes(barcode)

            # Assert
            # check the barcode returned and if the correct warning was raised
            self.assertEqual(results, barcode)
            self.assertTrue(any(issubclass(warning.category, UserWarning) for warning in w))
            self.assertTrue(any("Attribute 'name' is not 'Sequence'" in str(warning.message) for warning in w))

    def test_clarity_helper_get_barcode_from_reagenttypes_isvalid(self):
        """
        Pass a valid input to method
        """
        # Setup
        barcode = "N701-N501 (TAAGGCGA-TAGATCGC)"
        results_barcode = "TAAGGCGA-TAGATCGC"

        # Test
        results = self.api.get_barcode_from_reagenttypes(barcode)

        # Assert
        assert results == results_barcode

    def test_clarity_helper_get_sample_barcode_from_runid_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_sample_barcode_from_runid(None)

    def test_clarity_helper_reformat_barcode_to_index_novalid_barcodes(self):
        """
        Pass None and an empty barcode to method
        """

        # Setup
        sample_info = {"sample1": {"barcode": None}, "sample2": {"barcode": ""}, "sample3": {"user": "No user", "barcode": "No Barcode"}}

        # Assert
        with warnings.catch_warnings(record=True) as warn:
            warnings.simplefilter("always")  # Catch all warnings
            self.api.reformat_barcode_to_index(sample_info)  # Call the function that raises a warning
            self.assertEqual(len(warn), 1)  # Check that a warning was raised
            self.assertIs(warn[-1].category, UserWarning)  # Check that it's a Warning

    def test_clarity_helper_reformat_barcode_to_index_isvalid(self):
        """
        Pass all different variations of barcode values within the sample info dict
        """

        # Setup
        sample_info = {
            "sample1": {"barcode": None},
            "sample2": {"barcode": "First Kit (GeneX-YGeneY)"},
            "sample3": {"project": "Project Info", "barcode": "Second Kit (CTTGTGCT-ACATACAC)"},
            "sample4": {"barcode": "Random Kit (SingleIndex)"},
            "sample5": {"info": "No barcode in dict"},
        }
        expected = {
            "sample2": {"index": "GeneX", "index2": "YGeneY"},
            "sample3": {"index": "CTTGTGCT", "index2": "ACATACAC"},
            "sample4": {"index": "SingleIndex", "index2": ""},
        }

        # Test
        result = self.api.reformat_barcode_to_index(sample_info)

        # Assert
        self.assertEqual(result, expected)

    def test_clarity_helper_collect_samplesheet_info_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.collect_samplesheet_info(None)


class TestClarityHelperLimsyWithFixtures:
    """Class for clarity tests with fixtures"""

    @pytest.fixture(scope="class")
    def api(self, request):
        """Setup API connection"""
        data_file_path = os.path.join(API_TEST_DATA, "mock_data", "helper-data.pkl")
        lims = ClarityHelperLimsMock(baseuri="https://asf-claritylims.thecrick.org")
        lims.load_tracked_requests(data_file_path)
        request.addfinalizer(lambda: lims.save_tracked_requests(data_file_path))
        yield lims

    @pytest.mark.parametrize("runid,expected", [("20240417_1729_1C_PAW45723_05bb74c5", 1), ("20240625_1734_2F_PAW20497_d0c3cbb5", 1)])
    def test_clarity_helper_get_artifacts_from_runid_valid(self, api, runid, expected):
        """
        Pass real run IDs and test expected number of artifacts back
        """

        # Test
        artifacts = api.get_artifacts_from_runid(runid)

        # Assert
        assert len(artifacts) == expected

    @pytest.mark.parametrize(
        "run_id,expected",
        [
            (
                "HWNT7BBXY",
                {
                    "HWNT7BBXY_1": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373229",
                        "lane": "1",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_2": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373230",
                        "lane": "2",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_3": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373231",
                        "lane": "3",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_4": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373232",
                        "lane": "4",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_5": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373233",
                        "lane": "5",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_6": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373234",
                        "lane": "6",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_7": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373235",
                        "lane": "7",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_8": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373236",
                        "lane": "8",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                },
            ),
            (
                "ASF_A05136-P27",
                {
                    "ASF_A05136-P27_1": {
                        "samples": ["SKO6875A940"],
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/SKO6875A940PA1",
                        "lane": "1",
                    },
                },
            ),
        ],
    )
    def test_clarity_helper_get_lane_from_runid_isvalid(self, api, run_id, expected):
        """
        Pass None to method
        """

        # Test
        results = api.get_lane_from_runid(run_id)
        print(results)

        # Assert
        assert results == expected

    @pytest.mark.parametrize("run_id,expected_sample_quantity", [("B_04-0004-S6_DT", 1), ("462-24_MPX-seq", 4)])  # Illumina  # ONT
    def test_clarity_helper_get_samples_from_artifacts_isvalid(self, api, run_id, expected_sample_quantity):
        """
        Pass real artifact IDs and test expected number of samples back
        """

        # Set up
        artifact = api.get_artifacts(name=run_id)

        # Test
        get_samples = api.get_samples_from_artifacts(artifact)
        print(get_samples)

        # Assert
        assert len(get_samples) == expected_sample_quantity

    @pytest.mark.parametrize(
        "sample_id,expected_dict",
        [
            (
                "KAN6921A20",
                {
                    "KAN6921A20": {
                        "sample_name": "99-005-0496_98-290_bp",
                        "group": "swantonc",
                        "user": "nnennaya.kanu",
                        "project_id": "DN24086",
                        "project_limsid": "KAN6921",
                        "project_type": "WGS",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "None",
                        "library_type": "ONT DNA Ligation",
                    }
                },
            ),  # ONT
            (
                "ALV729A45",
                {
                    "ALV729A45": {
                        "sample_name": "MAM040P_5",
                        "group": "ogarraa",
                        "user": "marisol.alvarez-martinez",
                        "project_id": "RN20066",
                        "project_limsid": "ALV729",
                        "project_type": "mRNA-Seq from RNA",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "RNA-Seq",
                        "library_type": "NEBNext_Low_Input_w_NEB_Ultra_II_FS",
                    }
                },
            ),
            (
                "SKO6875A940",
                {
                    "SKO6875A940": {
                        "sample_name": "L12120",
                        "group": "skoglundp",
                        "user": "pontus.skoglund",
                        "project_id": "PM24043",
                        "project_limsid": "SKO6875",
                        "project_type": "Other",
                        "reference_genome": "Other",
                        "data_analysis_type": "None",
                        "library_type": "Premade",
                    }
                },
            ),
        ],
    )
    def test_clarity_helper_get_sample_info_isvalid(self, api, sample_id, expected_dict):
        """
        Pass real sample IDs and test expected values in the dictionary output
        """

        # Set up
        sample = api.get_samples(search_id=sample_id)

        # Test
        get_info = api.get_sample_info(sample.id)
        print(get_info)

        # Assert
        assert get_info == expected_dict

    @pytest.mark.parametrize(
        "sample_id,expected_dict",
        [
            (
                "201C-2076956",
                {
                    "201C-2076956": {
                        "sample_name": "No_Template_Control",
                        "group": "sequencing",
                        "user": "ashley.fowler",
                        "project_id": None,
                        "project_limsid": None,
                        "project_type": None,
                        "reference_genome": None,
                        "data_analysis_type": None,
                        "library_type": None,
                    }
                },
            ),
        ],
    )
    def test_clarity_helper_get_sample_info_project_notexists(self, api, sample_id, expected_dict):
        """
        Pass real sample IDs and test expected values in the dictionary output
        """

        # Set up
        sample = api.get_samples(search_id=sample_id)

        # Test
        get_info = api.get_sample_info(sample.id)
        print(get_info)

        # Assert
        assert get_info == expected_dict

    @pytest.mark.parametrize(
        "runid,expected_sample_quantity",
        [
            ("20240417_1729_1C_PAW45723_05bb74c5", 4),
            ("HWNT7BBXY", 9),
            ("20240625_1734_2F_PAW20497_d0c3cbb5", 1),
            ("PAW45729_20240715_1306_20108e83", 48),
            ("ASF_A05136-P27", 1),
        ],
    )
    def test_clarity_helper_collect_sample_info_from_runid(self, api, runid, expected_sample_quantity):
        """
        Pass real run IDs and test expected number of samples stored in the dictionary output
        """

        # Test
        sample_dict = api.collect_sample_info_from_runid(runid)

        # Assert
        assert len(sample_dict) == expected_sample_quantity

    @pytest.mark.parametrize(
        "run_id,expected_dict",
        [
            (
                "20240417_1729_1C_PAW45723_05bb74c5",
                {
                    "VIV6902A1": {"barcode": "AAGAAAGTTGTCGGTGTCTTTGTG"},
                    "VIV6902A2": {"barcode": "TCGATTCCGTTTGTAGTCGTCTGT"},
                    "VIV6902A3": {"barcode": "GAGTCTTGTGTCCCAGTTACCAGG"},
                    "VIV6902A4": {"barcode": "TTCGGATTCTATCGTGTTTCCCTA"},
                },
            ),  # ONT
            ("20240625_1734_2F_PAW20497_d0c3cbb5", {}),
            (
                "20240807_1248_P2S-02348-A_PAW31464_90cccf6c",
                {
                    "SWA6667A7": {"barcode": "AAGAAAGTTGTCGGTGTCTTTGTG"},
                    "SWA6667A8": {"barcode": "TCGATTCCGTTTGTAGTCGTCTGT"},
                    "SWA6667A37": {"barcode": "GAGTCTTGTGTCCCAGTTACCAGG"},
                    "SWA6667A38": {"barcode": "TTCGGATTCTATCGTGTTTCCCTA"},
                    "SWA6667A39": {"barcode": "CTTGTCCAGGGTTTGTGTAACCTT"},
                    "SWA6667A41": {"barcode": "TTCTCGCAAAGGCAGAAAGTAGTC"},
                    "201C-2072202": {"barcode": "GTGTTACCGTGGGAATGAATCCTT"},
                },
            ),
        ],
    )
    def test_clarity_helper_get_sample_barcode_from_runid_isvalid(self, api, run_id, expected_dict):
        """
        Pass real run_id and test expected values in the dictionary output
        """

        # Test
        barcode_dict = api.get_sample_barcode_from_runid(run_id)
        # print(barcode_dict)

        # Assert
        assert barcode_dict == expected_dict

    @pytest.mark.parametrize(
        "run_id,expected_dict",
        [
            (
                "22G2JFLT4",
                {
                    "SOA6876A276": {"barcode": "AGACCAAT-AACTCCGG"},
                    "SOA6876A277": {"barcode": "ACCAAGAT-ATTGGTCT"},
                    "SOA6876A278": {"barcode": "ACTCTTGG-AGCTCCAA"},
                    "SOA6876A279": {"barcode": "CGTTCGCT-AGCGAACG"},
                    "SOA6876A280": {"barcode": "CGTAGATC-CAATTGCA"},
                    "SOA6876A281": {"barcode": "TGGTCCTG-TAACGAAG"},
                    "SOA6876A282": {"barcode": "AGCAAGGC-GCCGTCCG"},
                    "SOA6876A283": {"barcode": "TGGTTGAC-TCTGACTG"},
                    "SOA6876A284": {"barcode": "TGCTCTTC-AGGTCGGA"},
                    "SOA6876A285": {"barcode": "ATAATGGT-AGGTAGTT"},
                    "SOA6876A286": {"barcode": "TCAGTTAA-TTAACTGA"},
                    "SOA6876A287": {"barcode": "CCGGCGAC-TTCTAATG"},
                    "SOA6876A288": {"barcode": "GGCTTGAA-TTGACTAT"},
                    "SOA6876A289": {"barcode": "GGCCTCCT-AATCGCAT"},
                    "SOA6876A290": {"barcode": "CTATTCAT-AAGAGCGC"},
                    "SOA6876A291": {"barcode": "TCTACTAC-GTTAGCCG"},
                    "SOA6876A292": {"barcode": "ACCTTATT-AGGCGTCG"},
                    "SOA6876A293": {"barcode": "ACTGCAAG-AATAAGGT"},
                    "SOA6876A294": {"barcode": "TCGTTCGA-CCGCTAAC"},
                    "SOA6876A295": {"barcode": "CGCAAGCT-GAGCCTCC"},
                    "SOA6876A296": {"barcode": "GTTCAATA-GGAGCCAA"},
                    "SOA6876A297": {"barcode": "CCTTCAGG-CGCCAGTT"},
                    "SOA6876A298": {"barcode": "CTTCGTTA-CTTGAGTT"},
                    "SOA6876A299": {"barcode": "CTGGATAA-GCCTTGCT"},
                    "SOA6876A300": {"barcode": "GATCTTCC-TTGCGGAC"},
                    "SOA6876A301": {"barcode": "AGGCAAGG-ATTAATCC"},
                    "SOA6876A302": {"barcode": "CGGAATCA-TGCTTCGC"},
                    "SOA6876A303": {"barcode": "TGACGAAC-AATGCAAT"},
                    "SOA6876A304": {"barcode": "TCCTCCGC-CTAGGACC"},
                    "SOA6876A305": {"barcode": "ACTCCGCG-GTCGCGAA"},
                    "SOA6876A306": {"barcode": "CTCTGATG-CAATGGAT"},
                    "SOA6876A307": {"barcode": "GCTCTGCT-AGGAGGCC"},
                    "SOA6876A308": {"barcode": "TCAGGCGA-GATAAGTA"},
                    "SOA6876A309": {"barcode": "ACTATATA-ACTTACGG"},
                    "SOA6876A310": {"barcode": "GAACCGTT-AATCCGTC"},
                    "SOA6876A311": {"barcode": "GGCAGCCG-AAGGTTAT"},
                    "SOA6876A312": {"barcode": "AGCGGCAA-AGCAGGAG"},
                    "SOA6876A313": {"barcode": "TGACTCAA-CGGAACTT"},
                    "SOA6876A314": {"barcode": "GCATGGCG-CGACGTTA"},
                    "SOA6876A315": {"barcode": "AAGTTGGA-CGACGGCT"},
                    "SOA6876A316": {"barcode": "CGACGTAG-TGAGATCA"},
                    "SOA6876A317": {"barcode": "TCCGTATA-ATGCTTCT"},
                    "SOA6876A318": {"barcode": "CCATATAG-CGGTTCCA"},
                    "SOA6876A319": {"barcode": "CTGCTCGT-AGCAGAGC"},
                },
            ),  # custom barcode
            (
                "ASF_A05136-P27",
                {
                    "SKO6875A940": {"barcode": "ACTCCGCG-TAGTCGTT"},
                },
            ),  # custom barcode
            (
                "20240625_1734_2F_PAW20497_d0c3cbb5",
                {
                    "KAN6921A20": {"barcode": ""},
                },
            ),  # regular barcode
        ],
    )
    def test_get_sample_custom_barcode_from_runid_isvalid(self, api, run_id, expected_dict):
        """
        Pass real run_id and test expected values in the dictionary output
        """

        # Test
        barcode = api.get_sample_custom_barcode_from_runid(run_id)

        # Assert
        assert barcode == expected_dict

    @pytest.mark.parametrize("sample,expected_barcode", [("SKO6875A940", "ACTCCGCG-TAGTCGTT"), ("KAN6921A20", "")])  # Illumina  # ONT
    def test_clarity_helper_get_sample_custom_barcode_from_sampleid_isvalid(self, api, sample, expected_barcode):
        """
        Pass real artifact IDs and test expected number of samples back
        """

        # Test
        results = api.get_sample_custom_barcode_from_sampleid(sample)

        # Assert
        assert results == expected_barcode

    @pytest.mark.parametrize(
        "run_id,expected_dict",
        [
            (
                "20240417_1729_1C_PAW45723_05bb74c5",
                {
                    "VIV6902A1": {
                        "barcode": "AAGAAAGTTGTCGGTGTCTTTGTG",
                        "sample_name": "BR1_D0",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                        "library_type": "Oxford Nanopore",
                        "lanes": ["1"],
                    },
                    "VIV6902A2": {
                        "barcode": "TCGATTCCGTTTGTAGTCGTCTGT",
                        "sample_name": "BR1_D7",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                        "library_type": "Oxford Nanopore",
                        "lanes": ["1"],
                    },
                    "VIV6902A3": {
                        "barcode": "GAGTCTTGTGTCCCAGTTACCAGG",
                        "sample_name": "BR2_D0",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                        "library_type": "Oxford Nanopore",
                        "lanes": ["1"],
                    },
                    "VIV6902A4": {
                        "barcode": "TTCGGATTCTATCGTGTTTCCCTA",
                        "sample_name": "BR2_D7",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                        "library_type": "Oxford Nanopore",
                        "lanes": ["1"],
                    },
                },
            ),  # ONT
            (
                "HWNT7BBXY",
                {
                    "TLG66A2839": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "A_LTX265_NP_T1_FR1",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "CTGAGCCA",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
                    },
                    "TLG66A2840": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "L_LTX877_MR_T1_FR4",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "AGCCATGC",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
                    },
                    "TLG66A2841": {
                        "sample_name": "L_LTX877_MR_T1_FR5",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "project_type": "WES",
                        "barcode": "GTACGCAA",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
                    },
                    "TLG66A2842": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "A_LTX1310_MR_T1_FR3",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "AGTACAAG",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
                    },
                    "TLG66A2843": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "A_LTX1331_BR_T1_FR1",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "ACATTGGC",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
                    },
                    "TLG66A2844": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "U_LTX1350_BR_T1_FR3",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "ATTGAGGA",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
                    },
                    "TLG66A2845": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "U_LTX1335_SU_FLN1",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "GTCGTAGA",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
                    },
                    "TLG66A2848": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "U_LTX1335_BS_GL",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "AACGTGAT",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
                    },
                    "TLG66A2849": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "U_LTX1335_BP_LN1",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "CACTTCGA",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
                    },
                },
            ),  # Illumina
            (
                "ASF_A05136-P27",
                {
                    "SKO6875A940": {
                        "sample_name": "L12120",
                        "group": "skoglundp",
                        "user": "pontus.skoglund",
                        "project_id": "PM24043",
                        "project_limsid": "SKO6875",
                        "project_type": "Other",
                        "reference_genome": "Other",
                        "data_analysis_type": "None",
                        "barcode": "ACTCCGCG-TAGTCGTT",
                        "library_type": "Premade",
                        "lanes": ["1"],
                    },
                },
            ),  # Illumina, custom barcode
            (
                "20240625_1734_2F_PAW20497_d0c3cbb5",
                {
                    "KAN6921A20": {
                        "sample_name": "99-005-0496_98-290_bp",
                        "group": "swantonc",
                        "user": "nnennaya.kanu",
                        "project_id": "DN24086",
                        "project_limsid": "KAN6921",
                        "project_type": "WGS",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "None",
                        "barcode": "",
                        "library_type": "ONT DNA Ligation",
                        "lanes": ["1"],
                    }
                },
            ),  # ONT, no barcode info
        ],
    )
    def test_clarity_helper_collect_samplesheet_info_isvalid(self, api, run_id, expected_dict):
        """
        Pass real run_id and test expected values in the dictionary output
        """

        # Test
        merged_dict = api.collect_samplesheet_info(run_id)
        print(merged_dict)

        # Assert
        assert merged_dict == expected_dict
