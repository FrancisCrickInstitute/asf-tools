"""
Clarity API Child class with helper functions
"""

import logging
from typing import Optional

from asf_tools.api.clarity.clarity_lims import ClarityLims
from asf_tools.api.clarity.models import Artifact, ResearcherStub, Lab

log = logging.getLogger(__name__)

class ClarityHelperLims(ClarityLims):

    def get_artifacts_from_runid(self, run_id: str) -> list:
        if run_id is None:
            raise ValueError("Runid is None")

        # Check that the run ID exists in clarity
        run_containers = self.get_containers(name=run_id)
        if run_containers is None:
            raise KeyError("RunID does not exist")

        # Get a list of artifacts stubs
        run_artifacts = run_containers.placements
        return run_artifacts

    def get_samples_from_artifacts(self, artifacts_list: list) -> list:
        if artifacts_list is None:
            raise ValueError("artifacts_list is None")

        sample_list = []
        values = self.expand_stubs(artifacts_list, expansion_type = Artifact)
        for value_item in values:
            run_samples = value_item.samples
            sample_list.extend(run_samples)

        # Make the entries in sample_list unique
        unique_sample_list = list({obj.limsid: obj for obj in sample_list}.values())
        return unique_sample_list

    def get_sample_info(self, sample: str) -> dict:
        if sample is None:
            raise ValueError("The sample is None")
        sample_stub = self.get_samples(search_id = sample)
        # print(sample_stub)
        sample_name = sample_stub.name
        project_id = self.get_projects(search_id = sample_stub.project.id)
        project_id = project_id.name

        # user = self.expand_stub(sample, expansion_type = ResearcherStub)
        # user_name = user.submitter.first_name 
        # user_lastname = user.submitter.last_name
        # user_fullname = (user_name + '.' + user_lastname).lower()
        user_fullname = "placeholder.name"

        # lab = user.submitter.lab.name #shouldn't work
        lab = "placeholder_lab"

        sample_info = {}
        sample_info[sample_name] = {
            "group": lab, 
            "user": user_fullname, 
            "project_id": project_id
            }
        # print(sample_info)

        return sample_info
    
    def collect_sample_info_from_runid(self, run_id: str) -> dict:

        artifacts_list = self.get_artifacts_from_runid(run_id)
        sample_list = self.get_samples_from_artifacts(artifacts_list)
        # print(sample_list)

        sample_info = {}
        for sample_id in sample_list:
            # print(sample_id.id)
            info = self.get_sample_info(sample_id.id)
            sample_info.update(info)
        return sample_info

    # def test_sample_barcode(self):
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