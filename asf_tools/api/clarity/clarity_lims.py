"""
Genlogics Clarity specific API class
"""

import logging

from genologics.lims import Lims
from genologics.config import BASEURI, USERNAME, PASSWORD

log = logging.getLogger(__name__)


class ClarityLims(Lims):
    """
    Genlogics Clarity specific API class
    """

    def __init__(self, baseuri = None, username = None, password = None):
        # Init connection from config if they are not passed
        if baseuri is None:
            baseuri = BASEURI
        if username is None:
            username = USERNAME
        if password is None:
            password = PASSWORD

        super().__init__(baseuri, username, password)


    def get_artifacts_from_runid(self, run_id: str) -> list:
        if run_id is None:
            raise ValueError("Runid is None")
        
        # Check that the run ID exists in clarity
        run_container = self.get_containers(name=run_id)
        if len(run_container) == 0:
            raise KeyError("RunID does not exist")
        
        # run_artifacts = run_container.placements
        # run_artifacts = list(run_artifacts.values())
        
    # def get_samples_from_artifacts(self, artifacts_list: list) -> list:
    #     if artifacts_list is None:
    #         raise ValueError("The artifacts list is None")
        
    #     sample_list = []
    #     for value in artifacts_list:
    #         run_samples = value.samples
    #         sample_list.extend(run_samples)
    #     return sample_list
    
    # def get_sample_info(self, sample: str) -> dict:
    #     sample_name = sample.name
    #     lab = sample.submitter.lab.name
    #     user_name = sample.submitter.first_name
    #     user_lastname = sample.submitter.last_name
    #     user_fullname = (user_name + '.' + user_lastname).lower()
    #     project_id = sample.project.name
        
    #     sample_info = {}
    #     sample_info[sample_name] = {
    #         "group": lab, 
    #         "user": user_fullname, 
    #         "project_id": project_id
    #         }