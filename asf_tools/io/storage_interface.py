"""
A Single Interface for file/folder operations remote or local
"""

from enum import Enum
import logging
import os
import subprocess

from asf_tools.ssh.file_object import FileType
from asf_tools.ssh.nemo import Nemo
from asf_tools.io.utils import list_directory_names, check_file_exist


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

    def list_directories_with_links(self, path):
        dirlist = []
        if self.interface_type == InterfaceType.LOCAL:
            return list_directory_names(path)
        elif self.interface_type == InterfaceType.NEMO:
            dir_objs = self.interface.list_directory_objects(path)
            for obj in dir_objs:
                if obj.type == FileType.FOLDER:
                    dirlist.append(obj.name)
                elif obj.type == FileType.LINK:
                    if '.' not in obj.link_target.split('/')[-1]:
                        dirlist.append(obj.name)
        return dirlist

    def exists(self, path):
        if self.interface_type == InterfaceType.LOCAL:
            return os.path.exists(path)
        elif self.interface_type == InterfaceType.NEMO:
            return self.interface.exists(path)

    def exists_with_pattern(self, path, pattern):
        if self.interface_type == InterfaceType.LOCAL:
            return check_file_exist(path, pattern)
        elif self.interface_type == InterfaceType.NEMO:
            return self.interface.exists_with_pattern(path, pattern)

    def run_command(self, command):
        if self.interface_type == InterfaceType.NEMO:
            return self.interface.run_command(command)
        else:
            return subprocess.run(command, shell=True, check=True)
