"""
Clarity API Tests
"""

import os
import unittest
import pytest

from asf_tools.api.clarity.clarity_lims import ClarityLims

API_TEST_DATA = "tests/data/api/clarity"


class TestClarity(unittest.TestCase):
    """Class for testing the clarity api wrapper"""

    def setUp(self):
        self.api = ClarityLims()

    def test_clarity_load_credentials_valid(self):
        """
        Test credentials load properly
        """

        # Test
        credentials = self.api.load_credentials(os.path.join(API_TEST_DATA, "test_credentials.toml"))

        # Assert
        self.assertTrue("clarity" in credentials)
        self.assertEqual(credentials["clarity"]["baseuri"], "https://localhost:8080")
        self.assertEqual(credentials["clarity"]["username"], "test")
        self.assertEqual(credentials["clarity"]["password"], "password")



class TestClarityWithFixtures:
    """Class for clarity tests with fixtures"""

    @pytest.fixture(scope="class")
    def api(self):
        """Setup API connection"""
        yield ClarityLims()

    # @pytest.mark.parametrize("runid,expected", [
    #     ("20240417_1729_1C_PAW45723_05bb74c5", 1)
    # ])
    # def test_get_artifacts_from_runid_valid(self, api, runid, expected):
    #     """
    #     Pass real runids and test expected number back
    #     """

    #     # Test
    #     artifacts = api.get_artifacts_from_runid(runid)

    #     # Assert
    #     assert len(artifacts) == expected


# class TestClarityMocks:
#     """
#     Mock generation methods
#     """
#     @pytest.mark.only_run_with_direct_target
#     def test_mocking_generate_clarity_data(self):
#         """
#         Generates a new test data set from the api
#         """

#         MockClarityLims.generate_test_data(MOCK_API_DATA_DIR)

class TestClarityPrototype(unittest.TestCase):
    """
    Test class for prototype functions
    """

    def setUp(self):
        self.api = ClarityLims()

    @pytest.mark.only_run_with_direct_target
    def test_api(self):

        raise ValueError