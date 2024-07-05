"""
Clarity helper API Tests
"""

import os
import unittest

import pytest
from requests.exceptions import HTTPError

from asf_tools.api.clarity.models import Stub

from .mocks.clarity_helper_lims_mock import ClarityHelperLimsMock


API_TEST_DATA = "tests/data/api/clarity"


class TestClarityHelperLims(unittest.TestCase):
    """Class for testing the clarity api wrapper"""

    def setUp(self):
        self.api = ClarityHelperLimsMock()

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
        with self.assertRaises(HTTPError):
            self.api.get_samples_from_artifacts(artifacts_list)

    def test_clarity_helper_get_sample_info_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_sample_info(None)

    def test_clarity_helper_get_sample_barcode_from_runid_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_sample_barcode_from_runid(None)

    def test_clarity_helper_collect_ont_samplesheet_info_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.collect_ont_samplesheet_info(None)


class TestClarityHelperLimsyWithFixtures:
    """Class for clarity tests with fixtures"""

    @pytest.fixture(scope="class")
    def api(self, request):
        """Setup API connection"""
        data_file_path = os.path.join(API_TEST_DATA, "mock_data", "helper-data.pkl")
        lims = ClarityHelperLimsMock()
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

    @pytest.mark.parametrize("run_id,expected_sample_quantity", [("B_04-0004-S6_DT", 1), ("462-24_MPX-seq", 4)])  # Illumina  # ONT
    def test_clarity_helper_get_samples_from_artifacts_isvalid(self, api, run_id, expected_sample_quantity):
        """
        Pass real artifact IDs and test expected number of samples back
        """

        # Set up
        artifact = api.get_artifacts(name=run_id)

        # Test
        get_samples = api.get_samples_from_artifacts(artifact)

        # Assert
        assert len(get_samples) == expected_sample_quantity

    @pytest.mark.parametrize(
        "sample_id,expected_dict",
        [
            ("KAN6921A20", {"KAN6921A20": {"group": "swantonc", "user": "nnennaya.kanu", "project_id": "DN24086"}}),  # ONT
            ("ALV729A45", {"ALV729A45": {"group": "ogarraa", "user": "marisol.alvarez-martinez", "project_id": "RN20066"}}),
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

        # Assert
        assert get_info == expected_dict

    @pytest.mark.parametrize(
        "runid,expected_sample_quantity",
        [
            ("20240417_1729_1C_PAW45723_05bb74c5", 4),
            ("HWNT7BBXY", 9),
            ("20240625_1734_2F_PAW20497_d0c3cbb5", 1),
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
                    "VIV6902A1": {"barcode": "BC01 (AAGAAAGTTGTCGGTGTCTTTGTG)"},
                    "VIV6902A2": {"barcode": "BC02 (TCGATTCCGTTTGTAGTCGTCTGT)"},
                    "VIV6902A3": {"barcode": "BC03 (GAGTCTTGTGTCCCAGTTACCAGG)"},
                    "VIV6902A4": {"barcode": "BC04 (TTCGGATTCTATCGTGTTTCCCTA)"},
                },
            ),  # ONT
            ("20240625_1734_2F_PAW20497_d0c3cbb5", {}),
        ],
    )
    def test_clarity_helper_get_sample_barcode_from_runid_isvalid(self, api, run_id, expected_dict):
        """
        Pass real run_id and test expected values in the dictionary output
        """

        # Test
        barcode_dict = api.get_sample_barcode_from_runid(run_id)

        # Assert
        assert barcode_dict == expected_dict

    @pytest.mark.parametrize(
        "run_id,expected_dict",
        [
            (
                "20240417_1729_1C_PAW45723_05bb74c5",
                {
                    "VIV6902A1": {
                        "barcode": "BC01 (AAGAAAGTTGTCGGTGTCTTTGTG)",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                    },
                    "VIV6902A2": {
                        "barcode": "BC02 (TCGATTCCGTTTGTAGTCGTCTGT)",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                    },
                    "VIV6902A3": {
                        "barcode": "BC03 (GAGTCTTGTGTCCCAGTTACCAGG)",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                    },
                    "VIV6902A4": {
                        "barcode": "BC04 (TTCGGATTCTATCGTGTTTCCCTA)",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                    },
                },
            ),  # ONT
            (
                "HWNT7BBXY",
                {
                    "TLG66A2839": {"barcode": "SXT 40 H05 (CTGAGCCA)", "group": "swantonc", "user": "tracerx.tlg", "project_id": "TRACERx_Lung"},
                    "TLG66A2840": {"barcode": "SXT 41 A06 (AGCCATGC)", "group": "swantonc", "user": "tracerx.tlg", "project_id": "TRACERx_Lung"},
                    "TLG66A2841": {"barcode": "SXT 42 B06 (GTACGCAA)", "group": "swantonc", "user": "tracerx.tlg", "project_id": "TRACERx_Lung"},
                    "TLG66A2842": {"barcode": "SXT 43 C06 (AGTACAAG)", "group": "swantonc", "user": "tracerx.tlg", "project_id": "TRACERx_Lung"},
                    "TLG66A2843": {"barcode": "SXT 44 D06 (ACATTGGC)", "group": "swantonc", "user": "tracerx.tlg", "project_id": "TRACERx_Lung"},
                    "TLG66A2844": {"barcode": "SXT 45 E06 (ATTGAGGA)", "group": "swantonc", "user": "tracerx.tlg", "project_id": "TRACERx_Lung"},
                    "TLG66A2845": {"barcode": "SXT 46 F06 (GTCGTAGA)", "group": "swantonc", "user": "tracerx.tlg", "project_id": "TRACERx_Lung"},
                    "TLG66A2848": {"barcode": "SXT 03 C01 (AACGTGAT)", "group": "swantonc", "user": "tracerx.tlg", "project_id": "TRACERx_Lung"},
                    "TLG66A2849": {"barcode": "SXT 04 D01 (CACTTCGA)", "group": "swantonc", "user": "tracerx.tlg", "project_id": "TRACERx_Lung"},
                },
            ),  # Illumina
            (
                "20240625_1734_2F_PAW20497_d0c3cbb5",
                {"KAN6921A20": {"group": "swantonc", "user": "nnennaya.kanu", "project_id": "DN24086"}},
            ),  # ONT, no barcode info
        ],
    )
    def test_clarity_helper_collect_ont_samplesheet_info_isvalid(self, api, run_id, expected_dict):
        """
        Pass real run_id and test expected values in the dictionary output
        """

        # Test
        merged_dict = api.collect_ont_samplesheet_info(run_id)
        print(merged_dict)

        # Assert
        assert merged_dict == expected_dict


# class TestClarityHelperLimsPrototype(unittest.TestCase):
#     """
#     Test class for prototype functions
#     """

#     def setUp(self):  # pylint: disable=missing-function-docstring,invalid-name
#         self.api = ClarityHelperLims()

#     @pytest.mark.only_run_with_direct_target
#     def test_clarity_helper_lims_prototype(self):
#         """
#         Test prototyping method
#         """

#         # Test
#         data = self.api.collect_ont_samplesheet_info("20240625_1734_2F_PAW20497_d0c3cbb5")
#         print("-------")
#         print(data)
#         for key, value in data.items():
#             print(key)
#             print(value)

#         raise ValueError
