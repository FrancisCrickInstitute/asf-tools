"""
Clarity API Data Models
"""

# pylint: disable=missing-class-docstring

from typing import List
from pydantic import BaseModel, HttpUrl


class LabStub(BaseModel):
    uri: HttpUrl
    name: str

class ContainerStub(BaseModel):
    uri: HttpUrl
    limsid: str
    name: str
