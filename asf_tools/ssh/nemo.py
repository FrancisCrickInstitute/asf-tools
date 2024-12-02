"""
Establish an SSH connection to nemo and run commands.
"""

import logging

from fabric import Connection
from invoke.exceptions import UnexpectedExit

from asf_tools.ssh.file_object import FileObject


log = logging.getLogger(__name__)


class Nemo:
    """
    Establish an SSH connection to nemo and run commands.
    """

    def __init__(self, host, user, key_file=None, password=None):
        """
        Initialize the Nemo connection.

        :param host: The hostname of the remote server.
        :param user: The username to use for the connection.
        :param key_file: The path to the SSH key file (optional).
        :param password: The password for the connection (optional).
        """
        # Init
        self.host = host
        self.user = user
        self.key_file = key_file
        self.password = password
        self.connection = None

        # Establish the SSH connection with either key or password
        connect_kwargs = {}

        # Check if key or password is provided
        if self.key_file:
            connect_kwargs["key_filename"] = self.key_file
        elif self.password:
            connect_kwargs["password"] = self.password
        else:
            raise ValueError("Either key_file or password must be provided for authentication.")

        # Init the connection
        self.connection = Connection(host=self.host, user=self.user, connect_kwargs=connect_kwargs)

    def disconnect(self):
        """
        Close the SSH connection.
        """
        # Close the SSH connection
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        """
        Ensure connection is closed when the instance is deleted.
        """
        self.disconnect()

    def run_command(self, command: str) -> tuple:
        """
        Run a custom command on the HPC server.

        :param command: The command to run.
        :return: A tuple containing the command's stdout and stderr outputs.
        """
        # Run the command
        result = self.connection.run(command, hide=True)
        return result.stdout.strip(), result.stderr.strip()

    def list_directory_objects(self, directory: str) -> list:
        """
        List the contents of a directory.

        :param directory: The directory to list.
        :return: A list of FileObject instances representing the directory contents.

        Each FileObject contains the following fields:
        - name: The name of the file or directory.
        - owner: The owner of the file or directory.
        - group: The group associated with the file or directory.
        - size: The size of the file in bytes.
        - last_modified: The last modified date and time of the file or directory.
        - type: The type of the file (folder, file, link, other).
        - permissions: A dictionary representing the permissions for user, group, and others.
        - link_target: The target of the link if the file is a symbolic link.
        """
        # Lists the contents of the specified directory with detailed info
        result = self.connection.run(f"cd {directory} && ls -la --time-style=long-iso", hide=True)

        # Parse each line of the output and structure it
        files = []
        for line in result.stdout.strip().split("\n")[1:]:  # Skip the total line
            # Parse out the parts of the line
            parts = line.split()
            permissions = parts[0]
            owner = parts[2]
            if parts[4].isnumeric():
                group = parts[3]
                size = parts[4]
                last_modified = f"{parts[5]} {parts[6]}"
                name = " ".join(parts[7:])
            else:
                group = f"{parts[3]} {parts[4]}"
                size = parts[5]
                last_modified = f"{parts[6]} {parts[7]}"
                name = " ".join(parts[8:])

            # Create a FileObject instance
            file_object = FileObject(permissions, owner, group, size, last_modified, name)
            files.append(file_object)

        return files

    def list_directory(self, directory: str) -> list:
        """
        List the contents of a directory.

        :param directory: The directory to list.
        :return: A list of file paths in the directory.
        """

        # list directory objects, but just return a string path for each
        directory_objects = self.list_directory_objects(directory)
        return [file.name for file in directory_objects]

    def exists(self, path: str) -> bool:
        """
        Check if a file or directory exists.

        :param path: The path to check.
        :return: True if the file or directory exists, False otherwise.
        """
        # Check if the path exists
        try:
            self.connection.run(f"test -e {path}", hide=True)
        except UnexpectedExit:
            return False
        return True
