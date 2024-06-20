"""
Clarity Lims API Class
"""

import os
import logging
from typing import Optional, Dict
from urllib.parse import urlencode

import toml


log = logging.getLogger(__name__)


class ClarityLims():
    """
    Clarity API Interface
    """

    API_VERSION = "v2"

    def __init__(self, credentials_path: Optional[str] = None,
                 baseuri: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None):

        # Resolve credentials path
        resolved_cred_path = credentials_path
        if credentials_path is None:
            home_dir = os.path.expanduser("~")
            credentials_path = os.path.join(home_dir, ".clarityrc")

        # Try to load credentials from home folder
        if os.path.exists(resolved_cred_path):
            logging.debug(f"Loading credentials from {resolved_cred_path}")
            credentials = self.load_credentials(resolved_cred_path)
            self.baseuri = credentials["clarity"]["baseuri"]
            self.username = credentials["clarity"]["username"]
            self.password = credentials["clarity"]["password"]

        # Override if suppied via constructor
        if baseuri is not None:
            self.baseuri = baseuri
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password

        # Set auth
        self.api_auth = (self.username, self.password)

    def load_credentials(self, file_path: str) -> dict:
        """
        TODO
        """

        with open(file_path, "r", encoding="UTF-8") as file:
            return toml.load(file)

    def construct_uri(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> str:
        """
        TODO
        """

        uri = f"{self.baseuri}/api/{self.API_VERSION}/{endpoint}"
        if params:
            uri += '?' + urlencode(params)
        return uri