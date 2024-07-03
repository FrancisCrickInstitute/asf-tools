"""
Clarity API Data Models
"""

# pylint: disable=missing-class-docstring

from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class ClarityBaseModel(BaseModel):
    id: Optional[str] = None

    @model_validator(mode="before")
    def extract_id(cls, values):  # pylint: disable=no-self-argument
        """
        Set id of the object from the uri.
        """
        uri = values.get("uri")
        if uri:
            values["id"] = uri.split("/")[-1]
        return values

    def __str__(self):
        """
        Return a string representation of the model.
        """
        return "\n" + "\n".join(f"{key}: {value}" for key, value in self.model_dump().items())


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

    @model_validator(mode="before")
    def ensure_list(cls, values):  # pylint: disable=no-self-argument
        """
        Ensure placements is a list.
        """
        placements = values.get("placement")
        if isinstance(placements, dict):
            values["placement"] = [placements]
        return values


class Project(ClarityBaseModel):
    uri: str
    limsid: str
    name: str
    open_date: str
    researcher_uri: str = Field(alias="researcher")
    udf_fields: Optional[List[UdfField]] = Field(default_factory=list, alias="udf:field")
    file_fields: Optional[List[FileField]] = Field(default_factory=list, alias="file:file")

    @field_validator("researcher_uri", mode="before")
    def extract_researcher_uri(cls, values):  # pylint: disable=no-self-argument
        """
        Extract researcher URI.
        """
        if isinstance(values, dict) and "uri" in values:
            return values["uri"]
        return values


class Location(ClarityBaseModel):
    container: Stub
    value: str


class ResearcherStub(ClarityBaseModel):
    uri: str
    first_name: str = Field(alias="first-name")
    last_name: str = Field(alias="last-name")


class Researcher(ClarityBaseModel):
    uri: str
    first_name: str
    last_name: str
    initials: str
    email: str
    lab: Stub


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
    # reagent_labels: Optional[List[str]] = Field(alias="reagent_label", default_factory=list)
    control_type: Optional[Stub] = None
    udf_fields: Optional[List[UdfField]] = Field(default_factory=list, alias="udf:field")
    file_fields: Optional[List[FileField]] = Field(default_factory=list, alias="file:file")
    artifact_group: Optional[List[Stub]] = Field(default_factory=list)
    workflow_stages: Optional[List[Stub]] = Field(default_factory=list)
    demux: Optional[Stub] = None

    # @field_validator("reagent_labels", mode="before")
    # def extract_reagent_labels(cls, values):  # pylint: disable=no-self-argument
    #     """
    #     Reagent label is nested name
    #     """
    #     if isinstance(values, dict) and 'name' in values:
    #         return values['name']
    #     if isinstance(values, list):
    #         return [d["name"] for d in values]

    @field_validator("workflow_stages", mode="before")
    def extract_workflow_stages(cls, values):  # pylint: disable=no-self-argument
        """
        Workflow stages is nested
        """
        if values is None:
            return values
        values = values["workflow-stage"]
        if isinstance(values, dict):
            values = [values]
        return [Stub(**item) for item in values]

    @field_validator("samples", mode="before")
    def extract_samples(cls, values):  # pylint: disable=no-self-argument
        """
        Sample is one item sometimes
        """
        if isinstance(values, dict):
            return [values]
        return values

    @field_validator("artifact_group", mode="before")
    def extract_group(cls, values):  # pylint: disable=no-self-argument
        """
        artifact_group is one item sometimes
        """
        if isinstance(values, dict):
            return [values]
        return values

    @field_validator("udf_fields", mode="before")
    def udf_fields(cls, values):  # pylint: disable=no-self-argument
        """
        udf_fields is one item sometimes
        """
        if isinstance(values, dict):
            return [values]
        return values


class Sample(ClarityBaseModel):
    limsid: str
    uri: str
    name: str
    date_received: str
    project: Stub
    submitter: Stub
    artifact: Optional[Stub] = None
    udf_fields: Optional[List[UdfField]] = Field(default_factory=list, alias="udf:field")


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
    udf_fields: Optional[List[UdfField]] = Field(default_factory=list, alias="udf:field")
    file_fields: Optional[List[FileField]] = Field(default_factory=list, alias="file:file")

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

    @field_validator("udf_fields", mode="before")
    def ensure_list_udf_fields(cls, values):  # pylint: disable=no-self-argument
        """
        Make sure if one item is passed for input_output_map that we make it a list of one
        """
        if isinstance(values, dict):
            return [values]
        return values

    @field_validator("file_fields", mode="before")
    def ensure_list_file_fields(cls, values):  # pylint: disable=no-self-argument
        """
        Make sure if one item is passed for input_output_map that we make it a list of one
        """
        if isinstance(values, dict):
            return [values]
        return values

class Workflow(ClarityBaseModel):
    uri: str
    name: str
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
    uri: str
    name: str
    protocol_uri: str = Field(alias="protocol-uri")
    protocol_step_index: int = Field(alias="protocol-step-index")
    process_type: Stub = Field(alias="process-type")
    transitions: List[Transition] = Field(default_factory=list)

    @field_validator("transitions", mode="before")
    def extract_transitions(cls, values):  # pylint: disable=no-self-argument
        """
        Transitions is nested
        """
        if values is None:
            return []
        values = values["transition"]
        if isinstance(values, dict):
            values = [values]
        return [Transition(**item) for item in values]

    @field_validator("process_type", mode="before")
    def extract_process_type(cls, values):  # pylint: disable=no-self-argument
        """
        Extract process_type
        """
        values["name"] = values["#text"]
        return values


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


class QueueArtifact(ClarityBaseModel):
    limsid: str
    uri: str
    queue_time: str = Field(alias="queue-time")
    location: Location


class QueueStep(ClarityBaseModel):
    uri: str
    protocol_step_uri: str
    name: str
    artifacts: List[QueueArtifact] = Field(default_factory=list)

    @field_validator("artifacts", mode="before")
    def extract_stages(cls, values):  # pylint: disable=no-self-argument
        """
        Artifact is nested
        """
        if values is None:
            return []
        values = values["artifact"]
        if isinstance(values, dict):
            values = [values]
        return [QueueArtifact(**item) for item in values]
