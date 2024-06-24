"""
Clarity API Data Models
"""

# pylint: disable=missing-class-docstring

from typing import Optional, List, Union
from pydantic import BaseModel, Field, model_validator, field_validator


class ClarityBaseModel(BaseModel):
    id: Optional[str] = None

    @model_validator(mode='before')
    def extract_id(cls, values):  # pylint: disable=no-self-argument
        """
        Set id of the object from the uri
        """

        uri = values.get('uri')
        if uri:
            values['id'] = uri.split('/')[-1]
        return values

    def __str__(self):
        return "\n".join(f"{key}: {value}" for key, value in self.model_dump().items())


class Stub(ClarityBaseModel):
    uri: str
    name: Optional[str] = None
    limsid: Optional[str] = None
    status: Optional[str] = None


class UdfField(BaseModel):
    name: str
    type: str
    value: Union[str, int, bool] = Field(alias="#text")

class FileField(BaseModel):
    uri: str
    limsid: str

class Address(ClarityBaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postalCode: Optional[str] = None
    institution: Optional[str] = None
    department: Optional[str] = None


class Lab(ClarityBaseModel):
    uri: str
    name: str
    billing_address: Optional[Address] = None
    shipping_address: Optional[Address] = None
    website: Optional[str] = None


class ContainerType(ClarityBaseModel):
    name: str
    uri: str


class Placement(ClarityBaseModel):
    limsid: str
    uri: str
    value: str


class Container(ClarityBaseModel):
    limsid: str
    uri: str
    name: str
    type: ContainerType
    occupied_wells: int
    placements: List[Placement] = Field(alias="placement")
    state: str

    @model_validator(mode='before')
    def ensure_list(cls, values):  # pylint: disable=no-self-argument
        """
        Make sure if one item is passed for placements that we make it a list of one
        """
        placements = values.get('placement')
        if isinstance(placements, dict):
            values['placement'] = [placements]
        return values


class Project(ClarityBaseModel):
    uri: str
    limsid: str
    name: str
    open_date: str
    researcher_uri: str = Field(alias='researcher')
    udf_fields: Optional[List[UdfField]] = Field(default_factory=list, alias='udf:field')
    file_fields: Optional[List[FileField]] = Field(default_factory=list, alias='file:file')

    @field_validator("researcher_uri", mode="before")
    def extract_researcher_uri(cls, values):  # pylint: disable=no-self-argument
        """
        Researcher is nested uri
        """
        if isinstance(values, dict) and 'uri' in values:
            return values['uri']
        return values


class Location(ClarityBaseModel):
    container: Stub
    value: str


class ResearcherStub(ClarityBaseModel):
    uri: str
    first_name: str = Field(alias="first-name")
    last_name: str = Field(alias="last-name")


class Artifact(ClarityBaseModel):
    limsid: str
    uri: str
    name: str
    type: str
    output_type: str
    parent_process: Optional[Stub] = None
    qc_flag: Optional[str] = None
    location: Optional[Location] = None
    working_flag: Optional[bool] = None
    samples: Optional[List[Stub]] = Field(alias="sample", default_factory=list)
    reagent_labels: Optional[List[str]] = Field(alias="reagent_label", default_factory=list)
    control_type: Optional[Stub] = None
    udf_fields: Optional[List[UdfField]] = Field(default_factory=list, alias='udf:field')
    file_fields: Optional[List[FileField]] = Field(default_factory=list, alias='file:file')
    artifact_group: Optional[List[Stub]] = Field(default_factory=list)
    workflow_stages: Optional[List[Stub]] = Field(default_factory=list)
    demux: Optional[Stub] = None

    @field_validator("reagent_labels", mode="before")
    def extract_reagent_labels(cls, values):  # pylint: disable=no-self-argument
        """
        Reagent label is nested name
        """
        if isinstance(values, dict) and 'name' in values:
            return values['name']
        if isinstance(values, list):
            return [d["name"] for d in values]

    @field_validator("workflow_stages", mode="before")
    def extract_workflow_stages(cls, values):  # pylint: disable=no-self-argument
        """
        Workflow stages is nested
        """
        values = values["workflow-stage"]
        return [Stub(**item) for item in values]


class Sample(ClarityBaseModel):
    limsid: str
    uri: str
    name: str
    date_received: str
    project: Stub
    submitter: Stub
    artifact: Optional[Stub] = None
    udf_fields: Optional[List[UdfField]] = Field(default_factory=list, alias='udf:field')


class Input(ClarityBaseModel):
    limsid: str
    uri: str
    post_process_uri: str = Field(alias="post-process-uri")
    parent_process: Stub = Field(alias="parent-process")

class Output(ClarityBaseModel):
    limsid: str
    uri: str
    output_type: str = Field(alias="output-type")
    output_generation: Optional[str] = Field(alias="output-generation", default=None)


class InputOutputMap(ClarityBaseModel):
    input: Input
    output: Optional[Output] = None


class Process(ClarityBaseModel):
    limsid: str
    uri: str
    process_type: Stub = Field(alias="type")
    date_run: str
    technician: ResearcherStub
    input_output_map: List[InputOutputMap] = Field(default_factory=list)
    udf_fields: Optional[List[UdfField]] = Field(default_factory=list, alias='udf:field')
    file_fields: Optional[List[FileField]] = Field(default_factory=list, alias='file:file')

    @field_validator("process_type", mode="before")
    def extract_reagent_labels(cls, values):  # pylint: disable=no-self-argument
        """
        Process type has #text
        """
        values["name"] = values["#text"]
        return values

    @field_validator("input_output_map", mode="before")
    def ensure_list(cls, values):  # pylint: disable=no-self-argument
        """
        Make sure if one item is passed for input_output_map that we make it a list of one
        """
        if isinstance(values, dict):
            return [values]
        return values


class Workflow(ClarityBaseModel):
    name: str
    uri: str
    status: str
    protocols: List[Stub]
    stages: List[Stub]

    @field_validator("protocols", mode="before")
    def extract_protocol(cls, values):  # pylint: disable=no-self-argument
        """
        Protocols is nested
        """
        values = values["protocol"]
        return [Stub(**item) for item in values]

    @field_validator("stages", mode="before")
    def extract_stages(cls, values):  # pylint: disable=no-self-argument
        """
        Stages is nested
        """
        values = values["stage"]
        return [Stub(**item) for item in values]


class Transition(ClarityBaseModel):
    name: str
    sequence: str
    next_step_uri: str = Field(alias="next-step-uri")


class ProtocolStep(ClarityBaseModel):
    name: str
    uri: str
    protocol_uri: str = Field(alias="protocol-uri")
    protocol_step_index: int = Field(alias="protocol-step-index")
    transitions:  List[Transition] = Field(default_factory=list)

    @field_validator("transitions", mode="before")
    def extract_stages(cls, values):  # pylint: disable=no-self-argument
        """
        Transitions is nested
        """
        if values is None:
            return []
        values = values["transition"]
        if isinstance(values, dict):
            values = [values]
        return [Transition(**item) for item in values]


class Protocol(ClarityBaseModel):
    uri: str
    name: str
    index: str
    steps: List[ProtocolStep] = Field(default_factory=list)

    @field_validator("steps", mode="before")
    def extract_stages(cls, values):  # pylint: disable=no-self-argument
        """
        Steps is nested
        """
        values = values["step"]
        return [ProtocolStep(**item) for item in values]
