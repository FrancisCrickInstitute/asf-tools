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
        self.api = ClarityLims(credentials_path=os.path.join(API_TEST_DATA, "test_credentials.toml"))

    def test_clarity_load_credentials_valid(self):
        """
        Test credentials load properly from toml
        """

        # Test
        credentials = self.api.load_credentials(os.path.join(API_TEST_DATA, "test_credentials.toml"))

        # Assert
        self.assertTrue("clarity" in credentials)
        self.assertEqual(credentials["clarity"]["baseuri"], "https://localhost:8080")
        self.assertEqual(credentials["clarity"]["username"], "test")
        self.assertEqual(credentials["clarity"]["password"], "password")

    def test_clarity_init_check_loaded_credentials(self):
        """
        Test credentials load properly in init from file
        """

        # Test
        api = ClarityLims(credentials_path=os.path.join(API_TEST_DATA, "test_credentials.toml"))

        # Assert
        self.assertEqual(api.baseuri, "https://localhost:8080")
        self.assertEqual(api.username, "test")
        self.assertEqual(api.password, "password")

    def test_clarity_init_check_overide_credentials(self):
        """
        Test credentials load properly in init with overides
        """

        # Test
        api = ClarityLims(credentials_path=os.path.join(API_TEST_DATA, "test_credentials.toml"), baseuri="test1", username="test2", password="test3")

        # Assert
        self.assertEqual(api.baseuri, "test1")
        self.assertEqual(api.username, "test2")
        self.assertEqual(api.password, "test3")

    def test_clarity_construct_uri_endpoint(self):
        """
        Test construct URI endpoint
        """

        # Test
        uri = self.api.construct_uri("test")

        # Assert
        self.assertEqual(uri, "https://localhost:8080/test")

    def test_clarity_construct_uri_params(self):
        """
        Test construct URI endpoint
        """

        # Params
        params = { "userid" : "1234", "name" : "test" }

        # Test
        uri = self.api.construct_uri("users", params)

        # Assert
        self.assertEqual(uri, "https://localhost:8080/users?userid=1234&name=test")


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