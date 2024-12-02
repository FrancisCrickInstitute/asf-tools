"""
A Single Interface for file/folder operations remote or local
"""

from enum import Enum
import logging

from asf_tools.ssh.nemo import Nemo


log = logging.getLogger()

class InterfaceType(Enum):
    LOCAL = 1
    NEMO = 2

class StorageInterface:

    def __init__(self, interface_type: InterfaceType, **kwargs):

        # Init interface type
        self.interface_type = interface_type
        if self.interface_type == InterfaceType.LOCAL:
            self.interface = None
        elif self.interface_type == InterfaceType.NEMO:
            self.interface = Nemo(**kwargs)

