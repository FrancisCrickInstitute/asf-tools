"""
Clarity API Child class with helper functions
"""

import logging
from typing import Optional

from asf_tools.api.clarity.clarity_lims import ClarityLims

log = logging.getLogger(__name__)

class HelperLims(ClarityLims):

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
            raise ValueError("The artifacts list is None")
        print(artifacts_list)
        sample_list = []
        for value in artifacts_list:
            run_samples = value.samples
            sample_list.extend(run_samples)
        if len(sample_list) == 0:
            raise KeyError("No samples were found") # this would only raise an error if no samples were found. it doesn't handle errors from an invalid input correctly
        return sample_list
    
    def get_sample_info(self, sample: str) -> dict:
        if sample is None:
            raise ValueError("The sample is None")

        sample_name = sample.name
        lab = sample.submitter.lab.name
        user_name = sample.submitter.first_name
        user_lastname = sample.submitter.last_name
        user_fullname = (user_name + '.' + user_lastname).lower()
        project_id = sample.project.name
        
        sample_info = {}
        sample_info[sample_name] = {
            "group": lab, 
            "user": user_fullname, 
            "project_id": project_id
            }
        
        return sample_info
    
    # def collect_sample_info_from_runid(self, run_id: str) -> dict:

    #     artifacts_list = self.get_artifacts_from_runid(run_id)
    #     sample_list = self.get_samples_from_artifacts(artifacts_list)

    #     sample_info = {}
    #     for sample_id in sample_list:
    #         info = self.get_sample_info(sample_id)
    #         sample_info.update(info)
    #     return sample_info
    
    def get_tcustomindexing_false(self, process: str) -> list:
        if process is None:
            raise ValueError("Runid is None")
        
        if process.type.name != "T Custom Indexing":
            # Add parent processes to the stack for further processing
            parent_process_list = []
            for input, output in process.input_output_maps:
                if output["output-type"] == "Analyte":
                    parent_process = input.get('parent-process')
                    if parent_process:
                        parent_process_list.append(parent_process)
            return parent_process_list
        else:
            return False

    def get_tcustomindexing_true(self, process: str) -> dict:
        if process is None:
            raise ValueError("Runid is None")
        
        # Extract barcode information and store it in "sample_barcode_match"
        sample_barcode_match = {}
        for input, output in process.input_output_maps:
            if output["output-type"] == "Analyte":
                uri = output['uri']
                sample_info = uri.samples[0]
                sample_name = sample_info.id
                reagent_barcode = uri.reagent_labels
                sample_barcode_match[sample_name] = {"barcode": reagent_barcode}
        return sample_barcode_match

    # def get_sample_barcode(self, run_id: str) -> dict:
    #     if run_id is None:
    #         raise ValueError("Runid is None")
        
    #     artifacts_list = self.get_artifacts_from_runid(run_id)
    #     sample_barcode_dict = {}
    #     for artifact in artifacts_list:
    #         initial_process = artifact.parent_process
    #         if initial_process is None:
    #             raise ValueError("Initial process is None")
            
    #         visited_processes = set()
    #         stack = [initial_process]
    #         # print(stack)

    #         while stack:
    #             process = stack.pop()
    #             print(process)
    #             if process.id in visited_processes:
    #                 continue

    #             visited_processes.add(process.id)
    #             new_process = self.get_tcustomindexing_false(process)
    #             if new_process is not False:
    #                 stack.extend(new_process)
    #             if new_process is False:
    #                 sample_barcode_match = self.get_tcustomindexing_true(new_process)
    #                 sample_barcode_dict.update(sample_barcode_match)
    #     print(sample_barcode_dict)
    #     return sample_barcode_dict