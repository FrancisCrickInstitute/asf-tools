"""
Establish an SSH connection to nemo and run commands.
"""

import logging


from fabric import Connection
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
        # Init
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
        self.connection = Connection(
            host=self.host,
            user=self.user,
            connect_kwargs=connect_kwargs
        )

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

    def run_command(self, command):
        """
        Run a custom command on the HPC server.

        :param command: The command to run.
        :return: A tuple containing the command's stdout and stderr outputs.
        """
        # Run the command
        result = self.connection.run(command, hide=True)
        return result.stdout.strip(), result.stderr.strip()

    def list_directory(self, directory):
        """
        List the contents of a directory.

        :param directory: The directory to list.
        :return: A list of FileObject instances representing the directory contents.
        """
        # Lists the contents of the specified directory with detailed info
        result = self.connection.run(f'cd {directory} && ls -la --time-style=long-iso', hide=True)

        # Parse each line of the output and structure it
        files = []
        for line in result.stdout.strip().split('\n')[1:]:  # Skip the total line
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
