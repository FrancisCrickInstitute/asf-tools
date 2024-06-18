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


    def get_artifacts_from_runid(self, runid: str) -> list:
        if runid is None:
            raise ValueError("Runid is None")
        