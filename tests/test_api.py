"""
Clarity API Tests
"""

import os
import requests

import unittest
import pytest
from unittest.mock import Mock

from asf_tools.api.clarity.clarity_lims import ClarityLims
from asf_tools.api.clarity.models import (
    Stub,
    StubWithId,
    Container,
    Lab,
    Project
)

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
        self.assertEqual(uri, "https://localhost:8080/api/v2/test")

    def test_clarity_construct_uri_params(self):
        """
        Test construct URI endpoint
        """

        # Setup
        params = { "userid" : "1234", "name" : "test" }

        # Test
        uri = self.api.construct_uri("users", params)

        # Assert
        self.assertEqual(uri, "https://localhost:8080/api/v2/users?userid=1234&name=test")

    def test_clarity_validate_response_error(self):
        """
        Test validate response with fake data
        """

        # Setup
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.content = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<exc:exception xmlns:exc="http://genologics.com/ri/exception">\n    <message>Not found</message>\n</exc:exception>\n'

        # Test and Assert
        with self.assertRaises(requests.exceptions.HTTPError):
            self.api.validate_response(mock_response)

    def test_clarity_validate_response_ok(self):
        """
        Test validate response with fake data
        """

        # Setup
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.content = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

        # Test
        result = self.api.validate_response(mock_response)

        # Assert
        self.assertTrue(result)


    def test_clarity_get_params_from_args_with_none(self):
        """
        Get get args with none params
        """

        # Test
        params = self.api.get_params_from_args(name="test", param1=None, param2=None)

        # Assert
        self.assertDictEqual({"name": "test"}, params)

    def test_clarity_get_params_from_args_with_underscore(self):
        """
        Get get args with none params
        """

        # Test
        params = self.api.get_params_from_args(name="test", param1=None, param2=None, last_modified="test2")

        # Assert
        self.assertDictEqual({"name": "test", "last-modified": "test2"}, params)


class TestClarityWithFixtures:
    """Class for clarity tests with fixtures"""

    @pytest.fixture(scope="class")
    def api(self):
        """Setup API connection"""
        yield ClarityLims()

    @pytest.mark.parametrize("xml_path,outer_key,inner_key,type_name,expected_num", [
        ("labs.xml", "lab:labs", "lab", Stub, 141),
        ("containers.xml", "con:containers", "container", StubWithId, 249),
        ("projects.xml", "prj:projects", "project", StubWithId, 219)
    ])
    def test_clarity_get_single_page_instances(self, api, xml_path, outer_key, inner_key, type_name, expected_num):
        """
        Test instance construction
        """

        # Setup
        with open(os.path.join(API_TEST_DATA, "mock_xml", xml_path), 'r', encoding='utf-8') as file:
            xml_content = file.read()

        # Test
        data, next_page = api.get_single_page_instances(xml_content, outer_key, inner_key, type_name)  # pylint: disable=unused-variable

        # Assert
        assert len(data) == expected_num

    @pytest.mark.parametrize("xml_path,outer_key,type_name,instance_id", [
        ("container.xml", "con:container", Container, "27-6876"),
        ("lab.xml", "lab:lab", Lab, "602"),
        ("project.xml", "prj:project", Project, "GOL2")
    ])
    def test_clarity_get_instance(self, api, xml_path, outer_key, type_name, instance_id):
        """
        Test instance construction
        """

        # Setup
        with open(os.path.join(API_TEST_DATA, "mock_xml", xml_path), 'r', encoding='utf-8') as file:
            xml_content = file.read()

        # Test
        instance = api.get_single_instance(xml_content, outer_key, type_name)

        # print(instance)
        # raise ValueError

        # Assert
        assert instance.id == instance_id




class TestClarityLive():
    """
    Test class for live api tests
    """

    @pytest.fixture(scope="class")
    def api(self):
        """Setup API connection"""
        yield ClarityLims()

    @pytest.mark.only_run_with_direct_target
    @pytest.mark.parametrize("endpoint,params,status_codes", [
        ("labs", None, [200])
    ])
    def test_api_clarity_get(self, api, endpoint, params, status_codes):
        """
        Test Get against some endpoints
        """

        # Test
        data = api.get(endpoint, params, status_codes)

        # Assert
        assert data is not None



class TestClarityPrototype(unittest.TestCase):
    """
    Test class for prototype functions
    """

    def setUp(self):  # pylint: disable=missing-function-docstring,invalid-name
        self.api = ClarityLims()

    @pytest.mark.only_run_with_direct_target
    def test_prototype(self):

        # with open(os.path.join(API_TEST_DATA, "mock_xml", "labs.xml"), 'r', encoding='utf-8') as file:
        #     xml_content = file.read()

        # Test
        data = self.api.get_artifacts(id="2-8332743")
        print("-------")
        print(data)


        raise ValueError


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