#!/usr/bin/env python
"""
Set app version
"""

from importlib.metadata import PackageNotFoundError, version


# Set version from package information
__version__ = version("asf-tools")