"""
Genlogics Clarity specific mock API class
"""

import os
import pickle
from datetime import datetime

from asf_tools.api.clarity.clarity_lims import ClarityLims
from genologics.entities import Entity

# # Disable the __new__ method
# def disabled_new(cls, *args, **kwargs):
#     return object.__new__(cls)

# Entity.__new__ = disabled_new

class MockClarityLims(ClarityLims):
    """
    Genlogics Clarity specific mock API class
    """

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.labs = None
        self.containers = None

        super().__init__("http://localhost:8000", "test", "test")

    def _get_instances(self, klass, add_info=None, params=None):
        return None

    def get(self, uri, params=dict()):
        return None

    def get_labs(self, name=None, last_modified=None, udf=dict(), udtname=None, udt=dict(), start_index=None, add_info=False):
        # Load data
        if self.labs is None:
            with open(os.path.join(self.data_dir, "labs.pkl"), 'rb') as f:
                self.labs = pickle.load(f)

        return self.labs

    def get_containers(self, name=None, last_modified=None, udf=dict(), udtname=None, udt=dict(), start_index=None, add_info=False):
        """
        Overides get_containers and instead loads data from the test data folder
        """
        if self.containers is None:
            def custom_new(cls, lims=None, uri=None, id=None, _create_new=False):
                return object.__new__(cls)
            Entity.__new__ = custom_new

            with open(os.path.join(self.data_dir, "containers.pkl"), 'rb') as f:
                self.containers = pickle.load(f)

        if name is None:
            return self.containers

        for container in self.containers:
            print(container.name)

        # return [data for data in self.containers if data.name == name]
        return self.containers

    @staticmethod
    def generate_test_data(data_dir: str) -> None:
        """
        Generates a test data set and saves it to a folder using pickle
        """

        # Init
        cutoff = datetime(2024, 1, 1, 0, 0, 0).isoformat() + "Z"

        # Define test data
        # runids = [
        #     "20240417_1729_1C_PAW45723_05bb74c5"
        # ]

        # Init API
        lims = ClarityLims()

        # Save Labs
        labs = lims.get_labs()
        with open(os.path.join(data_dir, "labs.pkl"), 'wb') as file:
            pickle.dump(labs, file)

        # Save containers for specific runs ids
        containers = lims.get_containers(last_modified=cutoff)
        with open(os.path.join(data_dir, "containers.pkl"), 'wb') as file:
            pickle.dump(containers, file)
