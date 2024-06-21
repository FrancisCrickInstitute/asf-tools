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
    udf_fields: List[UdfField] = Field(default_factory=list, alias='udf:field')
    file_fields: List[FileField] = Field(default_factory=list, alias='file:file')

    @field_validator("researcher_uri", mode="before")
    def extract_researcher_uri(cls, values):  # pylint: disable=no-self-argument
        """
        Researcher is nested uri
        """
        if isinstance(values, dict) and 'uri' in values:
            return values['uri']
        return values
