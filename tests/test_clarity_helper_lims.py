"""
Clarity helper API Tests
"""

import unittest
from unittest.mock import patch, MagicMock
import pytest
from requests.exceptions import HTTPError
# from tests.mocks.mock_clarity_lims import MockClarityLims
# from asf_tools.api.clarity.clarity_lims import ClarityLims
from asf_tools.api.clarity.clarity_helper_lims import ClarityHelperLims
from asf_tools.api.clarity.models import Stub


# MOCK_API_DATA_DIR = "tests/data/api/clarity/mock_data"


class TestClarityHelperLims(unittest.TestCase):
    """Class for testing the clarity api wrapper"""

    def setUp(self):
        # self.api = ClarityLims()
        self.api = ClarityHelperLims()

    def test_get_artifacts_from_runid_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_artifacts_from_runid(None)

    def test_get_artifacts_from_runid_isinvalid(self):
        """
        Pass runid that does not exist
        """

        # Setup
        runid = 'fake_runid'

        # Test and Assert
        with self.assertRaises(KeyError):
            self.api.get_artifacts_from_runid(runid)

    def test_get_samples_from_artifacts_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_samples_from_artifacts(None)

    def test_get_samples_from_artifacts_isinvalid(self):
        """
        Pass an artifact that does not exist
        """

        # Setup
        artifacts_list = [Stub(id='TestID', uri='https://asf-claritylims.thecrick.org/api/v2/artifacts/TEST', name=None, limsid='TestID')]

        # Get a real artificact from the API that doesnt contain samples

        # Test and Assert
        with self.assertRaises(HTTPError):
            self.api.get_samples_from_artifacts(artifacts_list)

    def test_get_sample_info_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_sample_info(None)

    def test_get_sample_barcode_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_sample_barcode(None)

    def test_get_tcustomindexing_false_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_tcustomindexing_false(None)

    def test_get_tcustomindexing_true_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_tcustomindexing_true(None)


class TestClarityHelperLimsyWithFixtures:
    """Class for clarity tests with fixtures"""

    @pytest.fixture(scope="class")
    def api(self):
        """Setup API connection"""
        yield ClarityHelperLims()

    @pytest.mark.parametrize("runid,expected", [
        ("20240417_1729_1C_PAW45723_05bb74c5", 1)
    ])
    def test_get_artifacts_from_runid_valid(self, api, runid, expected):
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
    ]) # test 2 ONT and 2 Illumina
    def test_get_samples_from_artifacts_isvalid(self, api, run_id, expected_sample_quantity):
        """
        Pass real artifact IDs and test expected number of samples back
        """

        # Set up
        artifact = api.get_artifacts(name=run_id)
        # print(artifact)

        # Test 
        get_samples = api.get_samples_from_artifacts(artifact)
        # print(get_samples)

        # Assert
        assert len(get_samples) == expected_sample_quantity

    @pytest.mark.parametrize("sample_id,expected_dict", [
        # ("BR1_D0", {"BR1_D0": {"group": "Administrative Lab", "user": "api.tempest", "project_id": "RN24071"}}),
        # ("ALV729A45", {"MAM040P_5": {"group": "sequencing", "user": "robert.goldstone", "project_id": "RN20066"}})
        ("ALV729A45", {"MAM040P_5": {"group": "placeholder_lab", "user": "placeholder.name", "project_id": "RN20066"}})
    ])
    def test_get_sample_info_isvalid(self, api, sample_id, expected_dict):
        """
        Pass real sample IDs and test expected values in the dictionary output
        """
        
        # Set up
        sample = api.get_samples(search_id=sample_id)
        # print(sample)
        
        # Test 
        get_info = api.get_sample_info(sample.id)
        print(get_info)

        # Assert
        assert get_info == expected_dict

    @pytest.mark.parametrize("runid,expected_sample_quantity", [
            ("20240417_1729_1C_PAW45723_05bb74c5", 4),
            ('HWNT7BBXY',9)
    ])
    def test_collect_sample_info_from_runid(self, api, runid, expected_sample_quantity):
        """
        Pass real run IDs and test expected number of samples stored in the dictionary output
        """

        # Test
        sample_dict = api.collect_sample_info_from_runid(runid)

        # Assert
        assert len(sample_dict) == expected_sample_quantity

    @pytest.mark.parametrize("process,expected_list", [
        ("https://asf-claritylims.thecrick.org/api/v2/processes/24-2060556", False),
        ("https://asf-claritylims.thecrick.org/api/v2/processes/24-12760", 3)
    ])
    def test_get_tcustomindexing_false_isvalid(self, api, process, expected_list):
        """
        Pass real run IDs and test expected number of artifacts back
        """

        # Set up

        # Test
        artifacts = api.get_tcustomindexing_false(process)

        # Assert
        assert len(artifacts) == expected_list

    @pytest.mark.parametrize("process,expected_dict_len", [
        ("https://asf-claritylims.thecrick.org/api/v2/processes/24-2060556", 16)
        # ("24-2060556", 16)
    ])
    def test_get_tcustomindexing_true_isvalid(self, api, process, expected_dict_len):
        """
        Pass real run IDs and test expected number of artifacts back
        """

        # Set up
        artifact = api.get_artifacts(name=process)
        # artifact = api.get_processes(processlimsid=process)
        print(artifact)

        # Test
        artifacts = api.get_tcustomindexing_true(artifact)

        # Assert
        assert len(artifacts) == expected_dict_len

    @pytest.mark.parametrize("runid,expected_dict_len", [
        ("20240417_1729_1C_PAW45723_05bb74c5", 16)
        # ("24-2060556", 16)
    ])
    def test_get_sample_barcode_isvalid(self, api, runid, expected_dict_len):
        """
        Pass real run IDs and test expected number of artifacts back
        """

        # Test
        barcode_info = api.get_sample_barcode(runid)

        # Assert
        assert len(barcode_info) == expected_dict_len

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

# class TestClarityPrototype(unittest.TestCase):
#     """
#     Test class for prototype functions
#     """

#     def setUp(self):
#         self.api = ClarityLims()

#     @pytest.mark.only_run_with_direct_target
#     def test_clarity_api(self):
#         lims = ClarityLims()

#         run_id = "20240417_1729_1C_PAW45723_05bb74c5"
#         run_container = lims.get_containers(name=run_id)[0]
#         # print("Container")
#         # print(f"Name: {run_container.name}")
#         # print(f"Type: {run_container.type}")
#         # print(f"Wells: {run_container.occupied_wells}")
#         # print(f"Placements: {run_container.placements}")
#         # print(f"UDF: {run_container.udf}")
#         # print(f"UDT: {run_container.udt}")
#         # print(f"State: {run_container.state}")
        
#         # projects = lims.get_projects(name="RN24071")
#         # print(projects)

#         # get info required to build the samplesheet
#         run_placement = run_container.placements
#         run_placement = list(run_placement.values())
#         print(run_placement)

#         sample_list = []
#         for value in run_placement:
#             run_samples = value.samples
#             sample_list.extend(run_samples)
#         print(sample_list)

#         sample_info = {}
#         for sample in sample_list:
#             sample_name = sample.name
#             lab = sample.submitter.lab.name
#             user_name = sample.submitter.first_name
#             user_lastname = sample.submitter.last_name
#             user_fullname = (user_name + '.' + user_lastname).lower()
#             project_id = sample.project.name
#             # print(lab)
#             # print(user_fullname)
#             # print(project_id)

#             sample_info[sample_name] = {
#                 "group": lab, 
#                 "user": user_fullname, 
#                 "project_id": project_id
#                 }
#         # print(sample_info)
#         if not sample_info:
#             raise ValueError("No sample information found")

#         return sample_info

#     @pytest.mark.only_run_with_direct_target
#     def test_sample_barcode(self):
#         lims = ClarityLims()

#         run_id = "20240417_1729_1C_PAW45723_05bb74c5"
#         run_container = lims.get_containers(name=run_id)[0]
#         artifacts = lims.get_artifacts(containername=run_container.name)

#         for artifact in artifacts:
#             initial_process = artifact.parent_process
#             sample_barcode_match = {}

#             if initial_process is None:
#                 raise ValueError("Initial process is None")
#             visited_processes = set()
#             stack = [initial_process]
#             print(stack)

#             while stack:
#                 process = stack.pop()
#                 if process.id in visited_processes:
#                     continue

#                 visited_processes.add(process.id)

#                 if process.type.name != "T Custom Indexing":
#                     # print(process.type.name)
#                     # Add parent processes to the stack for further processing
#                     for input, output in process.input_output_maps:
#                         if output["output-type"] == "Analyte":
#                             parent_process = input.get('parent-process')
#                             if parent_process:
#                                 stack.append(parent_process)
#                 else:
#                     # Extract barcode information and store it in "sample_barcode_match"
#                     for input, output in process.input_output_maps:
#                         if output["output-type"] == "Analyte":
#                             uri = output['uri']
#                             sample_info = uri.samples[0]
#                             sample_name = sample_info.id
#                             reagent_barcode = uri.reagent_labels
#                             sample_barcode_match[sample_name] = {"barcode": reagent_barcode}
#                     print(sample_barcode_match)
                    
#                     # return sample_barcode_match
#         raise ValueError