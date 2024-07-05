"""
Child class of Clarity Helper Lims that scrapes data from the LIMS for mocking
"""

import logging
import os
import pickle
from urllib.parse import urlencode

from asf_tools.api.clarity.clarity_helper_lims import ClarityHelperLims


log = logging.getLogger(__name__)


class ClarityHelperLimsMock(ClarityHelperLims):
    """
    Child class of Clarity Helper Lims that scrapes data from the LIMS for mocking
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tracked_requests = {}

    def get_with_uri(self, uri, params=None, accept_status_codes=[200]):
        """
        Tracks the uri, params and response data or loads from store
        """

        full_uri = uri
        if params:
            full_uri += "?" + urlencode(params)

        if full_uri not in self.tracked_requests:
            data = super().get_with_uri(uri, params, accept_status_codes)
            log.debug(f"Logging data for {full_uri}")
            self.tracked_requests[full_uri] = {"uri": uri, "params": params, "data": data}
        else:
            data = self.tracked_requests[full_uri]["data"]

        return data

    def load_tracked_requests(self, filepath):
        """
        Load tracked requests from file
        """
        if os.path.exists(filepath):
            with open(filepath, "rb") as file:
                self.tracked_requests = pickle.load(file)
                log.debug(f"Loaded {len(self.tracked_requests)} requests")

    def save_tracked_requests(self, filepath):
        """
        Dump tracked requests to file
        """
        with open(filepath, "wb") as file:
            pickle.dump(self.tracked_requests, file)
            log.debug(f"Saved {len(self.tracked_requests)} requests")
