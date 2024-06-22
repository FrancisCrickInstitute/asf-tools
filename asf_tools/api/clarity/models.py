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
    name: str

class StubWithId(Stub):
    limsid: str

class StubIdOnly(ClarityBaseModel):
    uri: str
    limsid: str

class StubUriOnly(BaseModel):
    uri: str

# class StubNameOnly(ClarityBaseModel):
#     name: str

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
    container: StubIdOnly
    value: str


class WorkflowStage(ClarityBaseModel):
    uri: str
    name: str
    status: str


class Artifact(ClarityBaseModel):
    limsid: str
    uri: str
    name: str
    type: str
    output_type: str
    parent_process: Optional[StubIdOnly] = None
    qc_flag: Optional[str] = None
    location: Optional[Location] = None
    working_flag: Optional[bool] = None
    samples: Optional[List[StubIdOnly]] = Field(alias="sample", default_factory=list)
    reagent_labels: Optional[List[str]] = Field(alias="reagent_label", default_factory=list)
    control_type: Optional[Stub] = None
    udf_fields: Optional[List[UdfField]] = Field(default_factory=list, alias='udf:field')
    file_fields: Optional[List[FileField]] = Field(default_factory=list, alias='file:file')
    artifact_group: Optional[List[Stub]] = Field(default_factory=list)
    workflow_stages: Optional[List[WorkflowStage]] = Field(default_factory=list)
    demux: Optional[StubUriOnly] = None

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
        return [WorkflowStage(**item) for item in values]


class Sample(ClarityBaseModel):
    limsid: str
    uri: str
    name: str
    date_received: str
    project: StubIdOnly
    submitter: StubUriOnly
    artifact: Optional[StubIdOnly] = None
    udf_fields: Optional[List[UdfField]] = Field(default_factory=list, alias='udf:field')
