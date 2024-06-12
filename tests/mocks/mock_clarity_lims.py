"""
Genlogics Clarity specific mock API class
"""

import os
import pickle

from asf_tools.api.clarity.clarity_lims import ClarityLims

class MockClarityLims(ClarityLims):
    """
    Genlogics Clarity specific mock API class
    """

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.labs = None

        super().__init__("http://localhost:8000", "test", "test")

    def _get_instances(self, klass, add_info=None, params=None):
        return None

    def get_labs(self,name=None, last_modified=None, udf=dict(), udtname=None, udt=dict(), start_index=None, add_info=False):
        # Load data
        if self.labs is None:
            with open(os.path.join(self.data_dir, "labs.pkl"), 'rb') as f:
                self.labs = pickle.load(f)

        return self.labs

    @staticmethod
    def generate_test_data(data_dir: str) -> None:
        """
        Generates a test data set and saves it to a folder using pickle
        """

        # Init API
        lims = ClarityLims()

        # Save Labs
        labs = lims.get_labs()
        with open(os.path.join(data_dir, "labs.pkl"), 'wb') as file:
            pickle.dump(labs, file)
