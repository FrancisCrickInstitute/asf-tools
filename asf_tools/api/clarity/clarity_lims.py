"""
Clarity Lims API Class
"""

import os
import logging
from typing import Optional, Dict
from urllib.parse import urlencode
from xml.etree import ElementTree
import requests

import toml
import xmltodict


log = logging.getLogger(__name__)


class ClarityLims():
    """
    Clarity API Interface
    """

    API_VERSION = "v2"
    API_TIMEOUT = 16

    def __init__(self, credentials_path: Optional[str] = None,
                 baseuri: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None):

        # Resolve credentials path
        resolved_cred_path = credentials_path
        if resolved_cred_path is None:
            home_dir = os.path.expanduser("~")
            resolved_cred_path = os.path.join(home_dir, ".clarityrc")

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

        # Setup API Connection
        self.request_session = requests.Session()
        self.adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.request_session.mount('http://', self.adapter)

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

    def validate_response(self, response, accept_status_codes=[200]):
        """
        TODO
        """

        if response.status_code not in accept_status_codes:
            try:
                root = ElementTree.fromstring(response.content)
                node = root.find('message')
                if node is None:
                    response.raise_for_status()
                    message = f"{response.status_code}"
                else:
                    message = f"{response.status_code}: {node.text}"
                node = root.find('suggested-actions')
                if node is not None:
                    message += ' ' + node.text
            except ElementTree.ParseError:  # some error messages might not follow the xml standard
                message = response.content
            raise requests.exceptions.HTTPError(message, response=response)
        return True

    def get_with_uri(self, uri: str, params: Optional[Dict[str, str]] = None, accept_status_codes=[200]):
        """
        TODO
        """

        # Try to call api
        try:
            response = self.request_session.get(uri, params=params,
                                         auth=(self.username, self.password),
                                         headers={"accept": "application/xml"},
                                         timeout=self.API_TIMEOUT)
        except requests.exceptions.Timeout as e:
            raise type(e)(f"{str(e)}, Error trying to reach {uri}")

        # Validate the response
        self.validate_response(response, accept_status_codes)

        return response.content

    def get(self, endpoint: str, params: Optional[Dict[str, str]] = None, accept_status_codes=[200]):
        """
        TODO
        """

        # Construct uri
        uri = self.construct_uri(endpoint, params)

        # Call main get
        return self.get_with_uri(uri, params, accept_status_codes)

    def get_single_page_instances(self, xml_data: str, outer_key: str, inner_key: str, model_type):
        """
        TODO
        """

        # Parse data
        data_dict = xmltodict.parse(xml_data, process_namespaces=False)

        # Create instances
        instances = []
        for item in data_dict[outer_key][inner_key]:
            # Clean @ symbols from dict keys
            cleaned_item = {key.replace('@', ''): value for key, value in item.items()}

            # Create type
            data_item = model_type(**cleaned_item)
            instances.append(data_item)

        # Look for next page
        next_page = data_dict[outer_key].get('next-page')
        if next_page is not None:
            next_page = next_page["@uri"]

        # Return data and next page hook
        return instances, next_page

    def get_instances(self, outer_key: str, inner_key: str, model_type, endpoint: str, params: Optional[Dict[str, str]] = None, accept_status_codes=[200]):
        """
        TODO
        """

        # Get first page
        xml_data = self.get(endpoint, params, accept_status_codes)
        instances, next_page = self.get_single_page_instances(xml_data, outer_key, inner_key, model_type)

        # Cycle through pages
        while next_page is not None:
            xml_data = self.get_with_uri(next_page, params, accept_status_codes)
            new_instances, next_page = self.get_single_page_instances(xml_data, outer_key, inner_key, model_type)
            instances.extend(new_instances)
            break

        return instances
