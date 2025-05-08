"""
A Single Interface for file/folder operations remote or local
"""

import logging
import os
import stat
import subprocess
from enum import Enum

from asf_tools.io.utils import check_file_exist, list_directory_names
from asf_tools.ssh.file_object import FileType
from asf_tools.ssh.nemo import Nemo


# File permission constants
PERM777 = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH
PERM666 = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH

# Logger setup
log = logging.getLogger()


class InterfaceType(Enum):
    """
    Enum for specifying the type of storage interface.
    """

    LOCAL = 1
    NEMO = 2


class StorageInterface:
    """
    A class to provide a unified interface for file and folder operations,
    either locally or remotely via Nemo.
    """

    def __init__(self, interface_type: InterfaceType, **kwargs):
        """
        Initialize the StorageInterface.

        :param interface_type: The type of interface (LOCAL or NEMO).
        :param kwargs: Additional arguments for initializing the Nemo interface.
        """
        self.interface_type = interface_type
        if self.interface_type == InterfaceType.LOCAL:
            self.interface = None
        elif self.interface_type == InterfaceType.NEMO:
            self.interface = Nemo(**kwargs)

    def list_directory(self, path):
        """
        List the contents of a directory.

        :param path: The path to the directory.
        :return: A list of directory contents.
        """
        if self.interface_type == InterfaceType.LOCAL:
            return os.listdir(path)
        elif self.interface_type == InterfaceType.NEMO:
            return self.interface.list_directory(path)

    def list_directories_with_links(self, path: str, max_date=None):
        """
        List directories and their symbolic links.

        :param path: The path to the directory.
        :return: A list of directories and their symbolic links.
        """
        dirlist = []
        if self.interface_type == InterfaceType.LOCAL:
            return list_directory_names(path)
        elif self.interface_type == InterfaceType.NEMO:
            dir_objs = self.interface.list_directory_objects(path)
            if max_date:
                dir_objs = [obj for obj in dir_objs if obj.last_modified >= max_date]
            for obj in dir_objs:
                if obj.type == FileType.FOLDER:
                    dirlist.append(obj.name)
                elif obj.type == FileType.LINK:
                    if "." not in obj.link_target.split("/")[-1]:
                        dirlist.append(obj.name)
        return dirlist

    def exists(self, path):
        """
        Check if a file or directory exists.

        :param path: The path to check.
        :return: True if the file or directory exists, False otherwise.
        """
        if self.interface_type == InterfaceType.LOCAL:
            return os.path.exists(path)
        elif self.interface_type == InterfaceType.NEMO:
            return self.interface.exists(path)

    def exists_with_pattern(self, path, pattern):
        """
        Check if a file or directory exists within the path that matches the pattern.

        :param path: The path to check.
        :param pattern: The pattern to match.
        :return: True if the file or directory exists and matches the pattern, False otherwise.
        """
        if self.interface_type == InterfaceType.LOCAL:
            return check_file_exist(path, pattern)
        elif self.interface_type == InterfaceType.NEMO:
            return self.interface.exists_with_pattern(path, pattern)

    def run_command(self, command):
        """
        Run a custom command.

        :param command: The command to run.
        :return: The result of the command execution.
        """
        if self.interface_type == InterfaceType.NEMO:
            return self.interface.run_command(command)
        else:
            return subprocess.run(command, shell=True, check=True)

    def make_dirs(self, path):
        """
        Create a directory.

        :param path: The path of the directory to create.
        """
        if self.interface_type == InterfaceType.LOCAL:
            os.makedirs(path, exist_ok=True)
        elif self.interface_type == InterfaceType.NEMO:
            self.interface.make_dirs(path)

    def write_file(self, path, content):
        """
        Write content to a file.

        :param path: The path of the file to write.
        :param content: The content to write to the file.
        """
        if self.interface_type == InterfaceType.LOCAL:
            with open(path, "w", encoding="UTF-8") as f:
                f.write(content)
        elif self.interface_type == InterfaceType.NEMO:
            self.interface.write_file(path, content)

    def read_file(self, path):
        """
        Read the contents of a file.

        :param path: The path of the file to read.
        :return: The contents of the file.
        """
        if self.interface_type == InterfaceType.LOCAL:
            with open(path, "r", encoding="UTF-8") as f:
                return f.read()
        elif self.interface_type == InterfaceType.NEMO:
            return self.interface.read_file(path)

    def parse_permission_string(self, permission_string):
        """
        Parse a permission string into a chmod octal integer and numeric string.

        :param permission_string: The permission string to parse.
        :return: A tuple containing the chmod octal integer and numeric string.
        """
        if len(permission_string) % 3 != 0 or not all(c in "rwx-" for c in permission_string):
            raise ValueError("Invalid permission string. Use a format like 'rwxr-xr--'.")

        modes = [
            (stat.S_IRUSR, "r"),
            (stat.S_IWUSR, "w"),
            (stat.S_IXUSR, "x"),
            (stat.S_IRGRP, "r"),
            (stat.S_IWGRP, "w"),
            (stat.S_IXGRP, "x"),
            (stat.S_IROTH, "r"),
            (stat.S_IWOTH, "w"),
            (stat.S_IXOTH, "x"),
        ]

        # Convert permission string to a chmod octal integer
        perm = 0
        for i, (mode, char) in enumerate(modes):
            if permission_string[i] == char:
                perm |= mode

        # Convert permission string to numeric (e.g., 'rwxr-xr--' -> 754)
        numeric_perm = ""
        for i in range(0, len(permission_string), 3):
            group = permission_string[i : i + 3]
            group_value = 0
            if group[0] == "r":
                group_value += 4
            if group[1] == "w":
                group_value += 2
            if group[2] == "x":
                group_value += 1
            numeric_perm += str(group_value)
        return perm, numeric_perm

    def chmod(self, path, permission_string):
        """
        Set the permissions of a file or directory.

        :param path: The path of the file or directory.
        :param permission_string: The permissions to set.
        """
        if self.interface_type == InterfaceType.LOCAL:
            perm, _ = self.parse_permission_string(permission_string)
            os.chmod(path, perm)
        elif self.interface_type == InterfaceType.NEMO:
            _, num_perm = self.parse_permission_string(permission_string)
            self.interface.chmod(path, num_perm)

    def walk(self, path):
        """
        Walk through a directory and yield all files.
        """
        if self.interface_type == InterfaceType.LOCAL:
            for root, folders, files in os.walk(path):
                yield root, folders, files
        elif self.interface_type == InterfaceType.NEMO:
            for root, folders, files in self.interface.walk(path):
                yield root, folders, files
