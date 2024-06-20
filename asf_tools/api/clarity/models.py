"""
Clarity API Data Models
"""

# pylint: disable=missing-class-docstring

from typing import List
from pydantic import BaseModel, HttpUrl

class ClarityBaseMode(BaseModel):
    def __str__(self):
        return "\n".join(f"{key}: {value}" for key, value in self.model_dump().items())

class LabStub(ClarityBaseMode):
    uri: HttpUrl
    name: str

class ContainerStub(ClarityBaseMode):
    uri: HttpUrl
    limsid: str
    name: str

class ContainerType(ClarityBaseMode):
    name: str
    uri: HttpUrl

class Placement(ClarityBaseMode):
    limsid: str
    uri: HttpUrl
    value: str

class Container(ClarityBaseMode):
    limsid: str
    uri: HttpUrl
    name: str
    type: ContainerType
    occupied_wells: int
    placements: List[Placement]
    state: str
