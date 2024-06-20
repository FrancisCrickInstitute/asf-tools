"""
Clarity API Data Models
"""

# pylint: disable=missing-class-docstring

from typing import List
from pydantic import BaseModel, HttpUrl


class Lab(BaseModel):
    uri: HttpUrl
    name: str
