#!/usr/bin/env python
"""
Set app version
"""

from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("asf-tools")
except PackageNotFoundError:
    __version__ = "0.0.0"
