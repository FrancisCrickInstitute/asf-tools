"""
Clarity API Data Models
"""

# pylint: disable=missing-class-docstring

from typing import Optional, List, Dict, ClassVar, Union
from pydantic import BaseModel, model_validator

class ClarityBaseModel(BaseModel):
    id: Optional[str] = None
    replacements: ClassVar[Dict] = {}

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

class LabStub(ClarityBaseModel):
    uri: str
    name: str

class ContainerStub(ClarityBaseModel):
    uri: str
    limsid: str
    name: str

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
    replacements: ClassVar[Dict] = {"placement": "placements"}
    limsid: str
    uri: str
    name: str
    type: ContainerType
    occupied_wells: int
    placements: Union[List[Placement], Placement]
    state: str
