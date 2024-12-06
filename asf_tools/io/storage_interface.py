"""
A Single Interface for file/folder operations remote or local
"""

from enum import Enum
import logging
import os
import subprocess

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

    def list_directory(self, path):
        if self.interface_type == InterfaceType.LOCAL:
            return os.listdir(path)
        elif self.interface_type == InterfaceType.NEMO:
            return self.interface.list_directory(path)

    def exists(self, path):
        if self.interface_type == InterfaceType.LOCAL:
            return os.path.exists(path)
        elif self.interface_type == InterfaceType.NEMO:
            return self.interface.exists(path)

    def run_command(self, command):
        if self.interface_type == InterfaceType.NEMO:
            return self.interface.run_command(command)
        else:
            return subprocess.run(command, shell=True, check=True)
