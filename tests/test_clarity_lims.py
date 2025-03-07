"""
Clarity API Tests
"""
# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

import os
import unittest
from assertpy import assert_that
from unittest.mock import Mock

import pytest
import requests

from asf_tools.api.clarity.clarity_lims import ClarityLims
from asf_tools.api.clarity.models import (
    Artifact,
    Container,
    Lab,
    Process,
    Project,
    Protocol,
    QueueStep,
    Researcher,
    ResearcherStub,
    Sample,
    Stub,
    Workflow,
)
from tests.mocks.clarity_lims_mock import ClarityLimsMock


API_TEST_DATA = "tests/data/api/clarity"

# Create class level mock API
@pytest.fixture(scope="class", autouse=True)
def mock_credentials_clarity_api(request):
    api = ClarityLimsMock(credentials_path=os.path.join(API_TEST_DATA, "test_credentials.toml"))
    request.cls.api = api
    yield api

class TestClarity:
    """Class for testing the clarity api wrapper"""

    def test_clarity_api_load_credentials_valid(self):
        """
        Test credentials load properly from toml
        """

        # Test
        credentials = self.api.load_credentials(os.path.join(API_TEST_DATA, "test_credentials.toml"))

        # Assert
        assert_that(credentials).contains("clarity")
        assert_that(credentials["clarity"]["baseuri"]).is_equal_to("https://localhost:8080")
        assert_that(credentials["clarity"]["username"]).is_equal_to("test")
        assert_that(credentials["clarity"]["password"]).is_equal_to("password")

    def test_clarity_api_init_check_loaded_credentials(self):
        """
        Test credentials load properly in init from file
        """

        # Test
        api = ClarityLims(credentials_path=os.path.join(API_TEST_DATA, "test_credentials.toml"))

        # Assert
        assert_that(api.baseuri).is_equal_to("https://localhost:8080")
        assert_that(api.username).is_equal_to("test")
        assert_that(api.password).is_equal_to("password")

    def test_clarity_api_init_check_overide_credentials(self):
        """
        Test credentials load properly in init with overides
        """

        # Test
        api = ClarityLims(credentials_path=os.path.join(API_TEST_DATA, "test_credentials.toml"), baseuri="test1", username="test2", password="test3")

        # Assert
        assert_that(api.baseuri).is_equal_to("test1")
        assert_that(api.username).is_equal_to("test2")
        assert_that(api.password).is_equal_to("test3")

    def test_clarity_api_construct_uri_endpoint(self):
        """
        Test construct URI endpoint
        """

        # Test and Assert
        assert_that(self.api.construct_uri("test")).is_equal_to("https://localhost:8080/api/v2/test")

    def test_clarity_api_validate_response_error(self):
        """
        Test validate response with fake data
        """

        # Setup
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.content = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<exc:exception xmlns:exc="http://genologics.com/ri/exception">\n    <message>Not found</message>\n</exc:exception>\n'  # pylint: disable=line-too-long

        # Test and Assert
        assert_that(self.api.validate_response).raises(requests.exceptions.HTTPError).when_called_with("https://localhost:8080/api", mock_response)

    def test_clarity_api_validate_response_ok(self):
        """
        Test validate response with fake data
        """

        # Setup
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.content = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

        # Test and Assert
        assert_that(self.api.validate_response("https://localhost:8080/api", mock_response)).is_true()

    def test_clarity_api_get_params_from_args_with_none(self):
        """
        Get get args with none params
        """

        # Test
        params = self.api.get_params_from_args(name="test", param1=None, param2=None)

        # Assert
        assert_that(params).is_equal_to({"name": "test"})

    def test_clarity_api_get_params_from_args_with_underscore(self):
        """
        Get get args with none params
        """

        # Test
        params = self.api.get_params_from_args(name="test", param1=None, param2=None, last_modified="test2")

        # Assert
        assert_that(params).is_equal_to({"name": "test", "last-modified": "test2"})

    @pytest.mark.parametrize(
        "xml_path,outer_key,inner_key,type_name,expected_num",
        [
            ("labs.xml", "lab:labs", "lab", Stub, 141),
            ("containers.xml", "con:containers", "container", Stub, 249),
            ("projects.xml", "prj:projects", "project", Stub, 219),
            ("artifacts.xml", "art:artifacts", "artifact", Stub, 828),
            ("samples.xml", "smp:samples", "sample", Stub, 333),
            ("processes.xml", "prc:processes", "process", Stub, 453),
            ("workflows.xml", "wkfcnf:workflows", "workflow", Stub, 27),
            ("researchers.xml", "res:researchers", "researcher", ResearcherStub, 82),
        ],
    )
    def test_clarity_api_get_single_page_instances(
        self, xml_path, outer_key, inner_key, type_name, expected_num
    ):  # pylint: disable=too-many-positional-arguments
        """
        Test instance construction
        """

        # Setup
        with open(os.path.join(API_TEST_DATA, "mock_xml", xml_path), "r", encoding="utf-8") as file:
            xml_content = file.read()

        # Test
        data, next_page = self.api.get_single_page_instances(xml_content, outer_key, inner_key, type_name)  # pylint: disable=unused-variable

        # Assert
        assert_that(data).is_length(expected_num)

    @pytest.mark.parametrize(
        "xml_path,outer_key,type_name,instance_id",
        [
            ("container.xml", "con:container", Container, "27-6876"),
            ("lab.xml", "lab:lab", Lab, "602"),
            ("researcher.xml", "res:researcher", Researcher, "4"),
            ("project.xml", "prj:project", Project, "GOL2"),
            ("artifact.xml", "art:artifact", Artifact, "2-8332743?state=5959893"),
            ("artifact_2.xml", "art:artifact", Artifact, "STR6918A110PA1?state=5982061"),
            ("artifact_3.xml", "art:artifact", Artifact, "92-8332746?state=5959896"),
            ("sample.xml", "smp:sample", Sample, "VIV6902A1"),
            ("process.xml", "prc:process", Process, "24-39409"),
            ("workflow.xml", "wkfcnf:workflow", Workflow, "56"),
            ("protocol.xml", "protcnf:protocol", Protocol, "1"),
            ("queue_step.xml", "que:queue", QueueStep, "60"),
        ],
    )
    def test_clarity_api_get_instance(self, xml_path, outer_key, type_name, instance_id):  # pylint: disable=too-many-positional-arguments
        """
        Test instance construction
        """

        # Setup
        with open(os.path.join(API_TEST_DATA, "mock_xml", xml_path), "r", encoding="utf-8") as file:
            xml_content = file.read()

        # Test
        instance = self.api.get_single_instance(xml_content, outer_key, type_name)

        # Assert
        assert_that(instance.id).is_equal_to(instance_id)


class TestClarityEndpoints:
    """
    Test class for pulling data from API endpoints
    """

    @pytest.fixture(scope="class")
    def api(self, request):
        """Setup API connection"""
        data_file_path = os.path.join(API_TEST_DATA, "mock_data", "data.pkl")
        lims = ClarityLimsMock(baseuri="https://asf-claritylims.thecrick.org")
        lims.load_tracked_requests(data_file_path)
        request.addfinalizer(lambda: lims.save_tracked_requests(data_file_path))
        yield lims

    @pytest.mark.parametrize(
        "func_name,search_id",
        [
            ("get_labs", None),
            ("get_labs", "2"),
            ("get_researchers", None),
            ("get_projects", "GOL2"),
            ("get_containers", "27-6876"),
            ("get_artifacts", "2-8332743?state=5959893"),
            ("get_samples", "VIV6902A1"),
            ("get_processes", "24-39409"),
            ("get_workflows", None),
            ("get_protocols", None),
            ("get_workflows", "56"),
            ("get_protocols", "1"),
            ("get_queues", "60"),
        ],
    )
    def test_clarity_api_get_endpoints(self, api, func_name, search_id):
        """
        Test Get against endpoints
        """

        # Setup
        api_func = getattr(api, func_name)

        # Test
        data = api_func(search_id=search_id)
        print(data)

        # Assert
        if isinstance(data, list):
            assert_that(data).is_not_empty()
        assert_that(data).is_not_none()
        if search_id is not None:
            assert_that(data.id).is_equal_to(search_id)

    def test_clarity_api_get_stub_list_returns_none_invalid(self, api):
        """
        Test returns none when no results exist
        """

        # Test and Assert
        assert_that(api.get_stub_list(Lab, Stub, "labs", "lab:labs", "lab", name="TEST")).is_none()

    def test_clarity_api_get_stub_list_noexpand(self, api):
        """
        Test returns single stub no expansion
        """

        # Test
        data = api.get_stub_list(Lab, Stub, "labs", "lab:labs", "lab", name="babs", expand_stubs=False)

        # Assert
        assert_that(data).is_instance_of(Stub)

    def test_clarity_api_expand_stubs(self, api):
        """
        Test expand stubs works
        """

        # Setup
        labs = api.get_stub_list(Lab, Stub, "labs", "lab:labs", "lab")

        # Test and Assert
        assert_that(api.expand_stubs(labs, Lab)).is_length(len(labs))


class TestClarityPrototype(unittest.TestCase):
    """
    Test class for prototype functions
    """

    def setUp(self):  # pylint: disable=missing-function-docstring,invalid-name
        self.api = ClarityLims()

    @pytest.mark.only_run_with_direct_target
    def test_clarity_api_prototype(self):
        """
        Test prototyping method
        """

        # Test
        data = self.api.get_queues("60")
        print("-------")
        print(data)

        raise ValueError
