"""
Clarity API Tests
"""

import unittest
import pytest
from tests.mocks.mock_clarity_lims import MockClarityLims

MOCK_API_DATA_DIR = "tests/data/api/clarity/mock_data"


class TestClarity(unittest.TestCase):
    """Class for testing the clarity api wrapper"""

    def setUp(self):
        self.api = MockClarityLims()

    @pytest.mark.only_run_with_direct_target
    def test_mock_clarity_generate_data(self):
        """
        Generates a new test data set from the api
        """

        MockClarityLims.generate_test_data(MOCK_API_DATA_DIR)

    # def test_clarity_api(self):
    #     self.api.get_labs()
