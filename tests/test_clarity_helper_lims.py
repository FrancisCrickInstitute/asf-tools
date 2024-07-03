"""
Clarity helper API Tests
"""

import unittest
from unittest.mock import patch, MagicMock
import pytest
from requests.exceptions import HTTPError
from asf_tools.api.clarity.clarity_helper_lims import ClarityHelperLims
from asf_tools.api.clarity.models import Stub

class TestClarityHelperLims(unittest.TestCase):
    """Class for testing the clarity api wrapper"""

    def setUp(self):
        # self.api = ClarityLims()
        self.api = ClarityHelperLims()

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
        runid = 'fake_runid'

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
        artifacts_list = [Stub(id='TestID', uri='https://asf-claritylims.thecrick.org/api/v2/artifacts/TEST', name=None, limsid='TestID')]

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

    def test_clarity_helper_get_sample_barcode(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_sample_barcode(None)

    # def test_clarity_helper_get_sample_barcode_isnone(self):
    #     """
    #     Pass None to method
    #     """

    #     # Test and Assert
    #     with self.assertRaises(ValueError):
    #         self.api.get_sample_barcode(None)

    # def test_clarity_helper_get_tcustomindexing_false_isnone(self):
    #     """
    #     Pass None to method
    #     """

    #     # Test and Assert
    #     with self.assertRaises(ValueError):
    #         self.api.get_tcustomindexing_false(None)

    # def test_clarity_helper_get_tcustomindexing_true_isnone(self):
    #     """
    #     Pass None to method
    #     """

    #     # Test and Assert
    #     with self.assertRaises(ValueError):
    #         self.api.get_tcustomindexing_true(None)


class TestClarityHelperLimsyWithFixtures:
    """Class for clarity tests with fixtures"""

    @pytest.fixture(scope="class")
    def api(self):
        """Setup API connection"""
        yield ClarityHelperLims()

    @pytest.mark.parametrize("runid,expected", [
        ("20240417_1729_1C_PAW45723_05bb74c5", 1),
        # ("B_04-0004-S6_DT", 1)
    ])
    def test_clarity_helper_get_artifacts_from_runid_valid(self, api, runid, expected):
        """
        Pass real run IDs and test expected number of artifacts back
        """

        # Test
        artifacts = api.get_artifacts_from_runid(runid)
        print(artifacts)
        # Assert
        assert len(artifacts) == expected, f"Expected {expected} artifacts, but got {len(artifacts)}"

    @pytest.mark.parametrize("run_id,expected_sample_quantity", [
        ("B_04-0004-S6_DT", 1), # Illumina
        ("462-24_MPX-seq", 4) # ONT
    ])
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

    @pytest.mark.parametrize("sample_id,expected_dict", [
        # ("BR1_D0", {"BR1_D0": {"group": "Administrative Lab", "user": "api.tempest", "project_id": "RN24071"}}),
        # ("ALV729A45", {"MAM040P_5": {"group": "sequencing", "user": "robert.goldstone", "project_id": "RN20066"}})
        ("ALV729A45", {"MAM040P_5": {"group": "placeholder_lab", "user": "placeholder.name", "project_id": "RN20066"}})
    ])
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

    @pytest.mark.parametrize("runid,expected_sample_quantity", [
            ("20240417_1729_1C_PAW45723_05bb74c5", 4),
            ('HWNT7BBXY',9)
    ])
    def test_clarity_helper_collect_sample_info_from_runid(self, api, runid, expected_sample_quantity):
        """
        Pass real run IDs and test expected number of samples stored in the dictionary output
        """

        # Test
        sample_dict = api.collect_sample_info_from_runid(runid)

        # Assert
        assert len(sample_dict) == expected_sample_quantity

    @pytest.mark.parametrize("run_id,expected_dict", [
            ("20240417_1729_1C_PAW45723_05bb74c5", 4)
            # ('HWNT7BBXY',9)
    ])
    def test_clarity_helper_get_sample_barcode_isvalid(self, api, run_id, expected_dict):
        """
        Pass real sample IDs and test expected values in the dictionary output
        """

        # Test
        get_info = api.get_sample_barcode(run_id)
        # print(get_info)

        # Assert
        assert get_info == expected_dict

    # @pytest.mark.parametrize("process,expected_list", [
    #     ("https://asf-claritylims.thecrick.org/api/v2/processes/24-2060556", False),
    #     ("https://asf-claritylims.thecrick.org/api/v2/processes/24-12760", 3)
    # ])
    # def test_clarity_helper_get_tcustomindexing_false_isvalid(self, api, process, expected_list):
    #     """
    #     Pass real run IDs and test expected number of artifacts back
    #     """

    #     # Set up

    #     # Test
    #     artifacts = api.get_tcustomindexing_false(process)

    #     # Assert
    #     assert len(artifacts) == expected_list

    # @pytest.mark.parametrize("process,expected_dict_len", [
    #     ("https://asf-claritylims.thecrick.org/api/v2/processes/24-2060556", 16)
    #     # ("24-2060556", 16)
    # ])
    # def test_clarity_helper_get_tcustomindexing_true_isvalid(self, api, process, expected_dict_len):
    #     """
    #     Pass real run IDs and test expected number of artifacts back
    #     """

    #     # Set up
    #     artifact = api.get_artifacts(name=process)
    #     # artifact = api.get_processes(processlimsid=process)
    #     print(artifact)

    #     # Test
    #     artifacts = api.get_tcustomindexing_true(artifact)

    #     # Assert
    #     assert len(artifacts) == expected_dict_len

    # @pytest.mark.parametrize("runid,expected_dict_len", [
    #     ("20240417_1729_1C_PAW45723_05bb74c5", 16)
    #     # ("24-2060556", 16)
    # ])
    # def test_clarity_helper_get_sample_barcode_isvalid(self, api, runid, expected_dict_len):
    #     """
    #     Pass real run IDs and test expected number of artifacts back
    #     """

    #     # Test
    #     barcode_info = api.get_sample_barcode(runid)

    #     # Assert
    #     assert len(barcode_info) == expected_dict_len