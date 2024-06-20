"""
Clarity Lims API Class
"""

import logging
import toml

log = logging.getLogger(__name__)


class ClarityLims():
    """
    Clarity API Interface
    """

    def __init__(self, base_uri = None, username = None, password = None):
        self.baseuri = base_uri
        self.username = username
        self.password = password

    def load_credentials(self, filepath: str) -> dict:
        """
        TODO
        """

        with open(filepath, "r", encoding="UTF-8") as file:
            return toml.load(file)
