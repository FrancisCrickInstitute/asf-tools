"""
Clarity Lims API Class
"""

import os
import logging
from typing import Optional, Dict
from xml.etree import ElementTree
import requests

import toml
import xmltodict

from asf_tools.api.clarity.models import (
    ClarityBaseModel,
    Stub,
    Lab,
    Project,
    Container,
    Artifact,
    Sample,
    Process,
    Workflow,
    Protocol,
    QueueStep
)

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
        Load credentials from a TOML file.

        Args:
            file_path (str): Path to the TOML file containing credentials.

        Returns:
            dict: Dictionary containing the credentials.
        """
        with open(file_path, "r", encoding="UTF-8") as file:
            return toml.load(file)

    def construct_uri(self, endpoint: str) -> str:
        """
        Construct the full URI for an API endpoint

        Args:
            endpoint (str): The API endpoint.

        Returns:
            str: The constructed URI.
        """
        uri = f"{self.baseuri}/api/{self.API_VERSION}/{endpoint}"
        return uri

    def get_params_from_args(self, **kwargs) -> dict:
        """
        Convert keyword arguments to a dictionary suitable for API query parameters.

        This method converts keyword arguments to a dictionary, replacing underscores
        in the argument names with hyphens to match the expected format for API query
        parameters. Arguments with a value of None are excluded from the resulting dictionary.

        Args:
            **kwargs: Arbitrary keyword arguments representing query parameters.

        Returns:
            dict: A dictionary of query parameters with hyphens replacing underscores in the keys.
        """
        result = {}
        for key, value in kwargs.items():
            if value is None:
                continue
            result[key.replace('_', '-')] = value
        return result

    def validate_response(self, uri, response, accept_status_codes = [200]) -> bool:
        """
        Validate the HTTP response from the API.

        Args:
            response: The HTTP response object.
            accept_status_codes (list): List of acceptable status codes.

        Returns:
            bool: True if the response is valid, raises an HTTPError otherwise.
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
            raise requests.exceptions.HTTPError(uri + " - " + message, response=response)
        return True

    def get_with_uri(self, uri: str, params: Optional[Dict[str, str]] = None, accept_status_codes=[200]) -> bytes:
        """
        Perform a GET request to a specified URI with optional query parameters.

        Args:
            uri (str): The URI to send the GET request to.
            params (Optional[Dict[str, str]]): Optional dictionary of query parameters.
            accept_status_codes (list): List of acceptable status codes.

        Returns:
            bytes: The content of the response.
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
        self.validate_response(uri, response, accept_status_codes)

        return response.content

    def get(self, endpoint: str, params: Optional[Dict[str, str]] = None, accept_status_codes=[200]) -> bytes:
        """
        Perform a GET request to a specified API endpoint with optional query parameters.

        Args:
            endpoint (str): The API endpoint.
            params (Optional[Dict[str, str]]): Optional dictionary of query parameters.
            accept_status_codes (list): List of acceptable status codes.

        Returns:
            bytes: The content of the response.
        """
        # Construct uri
        uri = self.construct_uri(endpoint)

        # Call main get
        return self.get_with_uri(uri, params, accept_status_codes)

    def get_with_id(self, endpoint: str, item_id: str, params: Optional[Dict[str, str]] = None) -> bytes:
        """
        TODO
        """
        # Construct uri
        uri = self.construct_uri(f"{endpoint}/{item_id}")

        # Call main get
        return self.get_with_uri(uri, params)

    def get_single_page_instances(self, xml_data: str, outer_key: str, inner_key: str, model_type: ClarityBaseModel) -> list[ClarityBaseModel]:
        """
        Parse XML data to get instances of a specified model from a single page.

        Args:
            xml_data (str): The XML data as a string.
            outer_key (str): The outer key in the XML structure.
            inner_key (str): The inner key in the XML structure.
            model_type (ClarityBaseModel): The model type to instantiate.

        Returns:
            list[ClarityBaseModel]: A list of instances of the model type.
        """
        # Parse data
        data_dict = xmltodict.parse(xml_data, process_namespaces=False, attr_prefix='')
        inner_dict = data_dict[outer_key]
        if inner_key not in inner_dict:
            return [], None
        inner_dict = inner_dict[inner_key]

        # Create instances
        instances = []
        if isinstance(inner_dict, list):
            for item in inner_dict:
                # Create type
                data_item = model_type(**item)
                instances.append(data_item)
        if isinstance(inner_dict, dict):
            data_item = model_type(**inner_dict)
            instances.append(data_item)

        # Look for next page
        next_page = data_dict[outer_key].get('next-page')
        if next_page is not None:
            next_page = next_page["uri"]

        # Return data and next page hook
        return instances, next_page

    def get_instances(self, outer_key: str, inner_key: str, model_type: ClarityBaseModel, endpoint: str,
                      params: Optional[Dict[str, str]] = None, accept_status_codes=[200]):
        """
        Get instances of a specified model from an API endpoint, handling pagination.

        Args:
            outer_key (str): The outer key in the XML structure.
            inner_key (str): The inner key in the XML structure.
            model_type (ClarityBaseModel): The model type to instantiate.
            endpoint (str): The API endpoint.
            params (Optional[Dict[str, str]]): Optional dictionary of query parameters.
            accept_status_codes (list): List of acceptable status codes.

        Returns:
            list[ClarityBaseModel]: A list of instances of the model type.
        """
        # Get first page
        xml_data = self.get(endpoint, params, accept_status_codes)
        instances, next_page = self.get_single_page_instances(xml_data, outer_key, inner_key, model_type)

        # Cycle through pages
        while next_page is not None:
            xml_data = self.get_with_uri(next_page, params, accept_status_codes)
            new_instances, next_page = self.get_single_page_instances(xml_data, outer_key, inner_key, model_type)
            instances.extend(new_instances)

        return instances

    def get_single_instance(self, xml_data: str, outer_key: str, model_type: ClarityBaseModel) -> ClarityBaseModel:
        """
        Parse XML data to get a single instance of a specified model.

        Args:
            xml_data (str): The XML data as a string.
            outer_key (str): The outer key in the XML structure.
            model_type (ClarityBaseModel): The model type to instantiate.

        Returns:
            ClarityBaseModel: An instance of the model type.
        """
        # Parse data
        data_dict = xmltodict.parse(xml_data, process_namespaces=False, attr_prefix='')
        data_dict = data_dict[outer_key]

        # Set hyphons to underscores
        data_dict = {key.replace('-', '_'): value for key, value in data_dict.items()}

        # Create and return model
        instance = model_type(**data_dict)
        return instance

    def expand_stub(self, stub: ClarityBaseModel, outer_key: str, expansion_type: ClarityBaseModel) -> ClarityBaseModel:
        """
        Expand a stub instance to a full instance by retrieving additional data from the API.

        Args:
            stub (ClarityBaseModel): The stub instance to expand.
            outer_key (str): The outer key in the XML structure.
            expansion_type (ClarityBaseModel): The model type to instantiate for the expanded data.

        Returns:
            ClarityBaseModel: An instance of the model type.
        """
        # Expand stub
        xml_data = self.get_with_uri(stub.uri)
        return self.get_single_instance(xml_data, outer_key, expansion_type)

    def get_stub_list(self, model_type, stub_type, endpoint, single_key, outer_key, inner_key, search_id=None, **kwargs):
        """
        TODO
        """
        # Check if we have used an id
        if search_id is not None:
            xml_data = self.get_with_id(endpoint, search_id)
            return self.get_single_instance(xml_data, single_key, model_type)

        # Contruct params and get instances
        params = self.get_params_from_args(**kwargs)
        instances = self.get_instances(outer_key, inner_key, stub_type, endpoint, params)

        # Expand if only one result is returned
        if len(instances) == 1:
            return self.expand_stub(instances[0], single_key, model_type)
        return instances

    def get_labs(self, search_id=None, name=None, last_modified=None):
        """
        Retrieve lab instances from the API with optional filtering by name or last modified date.

        Args:
            search_id (Optional[str]): Search by id.
            name (Optional[str]): Filter by lab name.
            last_modified (Optional[str]): Filter by last modified date.

        Returns:
            list[Stub] or Lab: A list of lab stubs or a single expanded lab instance if only one result is found.
        """
        return self.get_stub_list(Lab, Stub, "labs", "lab:lab", "lab:labs", "lab", search_id=search_id,
                                  name=name, last_modifie=last_modified)

    def get_projects(self, search_id=None, name=None, open_date=None, last_modified=None):
        """
        Retrieve container instances from the API with optional filtering by name or last modified date.

        Args:
            search_id (Optional[str]): Search by id.
            name (Optional[str]): Filter by container name.
            open_date (Optional[str]): Opened since the open_date.
            last_modified (Optional[str]): Filter by last modified date.

        Returns:
            list[Stub] or Project: A list of project stubs or a single expanded project instance if only one result is found.
        """
        return self.get_stub_list(Project, Stub, "projects", "prj:project", "prj:projects", "project", search_id=search_id,
                            name=name, open_date=open_date, last_modified=last_modified)

    def get_containers(self, search_id=None, name=None, last_modified=None):
        """
        Retrieve container instances from the API with optional filtering by name or last modified date.

        Args:
            search_id (Optional[str]): Search by id.
            name (Optional[str]): Filter by container name.
            last_modified (Optional[str]): Filter by last modified date.

        Returns:
            list[Stub] or Container: A list of container stubs or a single expanded container instance if only one result is found.
        """
        return self.get_stub_list(Container, Stub, "containers", "con:container", "con:containers", "container", search_id=search_id,
                    name=name, last_modified=last_modified)

    def get_artifacts(self, search_id=None, name=None, art_type=None, process_type=None, artifact_flag_name=None, working_flag=None, 
                      qc_flag=None, sample_name=None, samplelimsid=None, artifactgroup=None, containername=None,
                      containerlimsid=None, reagent_label=None):
        """
        TODO
        """
        return self.get_stub_list(Artifact, Stub, "artifacts", "art:artifact", "art:artifacts", "artifact", search_id=search_id, 
                                  name=name, type=art_type, process_type=process_type, artifact_flag_name=artifact_flag_name,
                                  working_flag=working_flag, qc_flag=qc_flag, sample_name=sample_name, samplelimsid=samplelimsid,
                                  artifactgroup=artifactgroup, containername=containername, containerlimsid=containerlimsid, 
                                  reagent_label=reagent_label)

    def get_samples(self, search_id=None, name=None, project_name=None, projectlimsid=None):
        """
        TODO
        """
        return self.get_stub_list(Sample, Stub, "samples", "smp:sample", "smp:samples", "sample", search_id=search_id,
                    name=name, project_name=project_name, projectlimsid=projectlimsid)

    def get_processes(self, search_id=None, last_modified=None, process_type=None, inputartifactlimsid=None, 
                      techfirstname=None, techlastname=None, projectname=None):
        """
        TODO
        """
        return self.get_stub_list(Process, Stub, "processes", "prc:process", "prc:processes", "process", search_id=search_id,
                                  last_modified=last_modified, type=process_type, inputartifactlimsid=inputartifactlimsid,
                                  techfirstname=techfirstname, techlastname=techlastname, projectname=projectname)

    def get_workflows(self, search_id=None, name=None):
        """
        TODO
        """
        return self.get_stub_list(Workflow, Stub, "configuration/workflows", "wkfcnf:workflow", "wkfcnf:workflows", "workflow",
                                  search_id=search_id, name=name)

    def get_protocols(self, search_id=None, name=None):
        """
        TODO
        """
        return self.get_stub_list(Protocol, Stub, "configuration/protocols", "protcnf:protocol", "protcnf:protocols", "protocol",
                                  search_id=search_id, name=name)


    def get_queues(self, search_id=None, workflowname=None, workflowid=None, projectname=None, projectlimsid=None,
                   containername=None, containerlimsid=None, previousstepid=None):
        """
        TODO
        """
        params = self.get_params_from_args(workflowname=workflowname, workflowid=workflowid, projectname=projectname, projectlimsid=projectlimsid,
                                           containername=containername, containerlimsid=containerlimsid, previousstepid=previousstepid)
        xml_data = self.get_with_id("queues", search_id, params)
        return self.get_single_instance(xml_data, "que:queue", QueueStep)
