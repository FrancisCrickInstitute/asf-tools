"""
Clarity API Data Models
"""

# pylint: disable=missing-class-docstring

from typing import List, Optional
from pydantic import BaseModel, model_validator

class ClarityBaseMode(BaseModel):
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

class LabStub(ClarityBaseMode):
    uri: str
    name: str

class ContainerStub(ClarityBaseMode):
    uri: str
    limsid: str
    name: str

class Address(ClarityBaseMode):
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postalCode: Optional[str]
    institution: Optional[str]
    department: Optional[str]

class Lab(ClarityBaseMode):
    uri: str
    name: str
    billing_address: Optional[Address]
    shipping_address: Optional[Address]
    website: Optional[str]

class ContainerType(ClarityBaseMode):
    name: str
    uri: str

class Placement(ClarityBaseMode):
    limsid: str
    uri: str
    value: str

class Container(ClarityBaseMode):
    limsid: str
    uri: str
    name: str
    type: ContainerType
    occupied_wells: int
    placements: List[Placement]
    state: str
