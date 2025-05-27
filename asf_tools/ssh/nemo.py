"""
Establish an SSH connection to nemo and run commands.
"""

import io
import logging

import paramiko
from fabric import Connection
from invoke.exceptions import UnexpectedExit

from asf_tools.ssh.file_object import FileObject, FileType


log = logging.getLogger(__name__)


class Nemo:
    """
    Establish an SSH connection to nemo and run commands.
    """

    def __init__(self, host=None, user=None, key_file=None, key_string=None, password=None):
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
        self.key_string = key_string
        self.password = password
        self.connection = None

        # Establish the SSH connection with either key or password
        connect_kwargs = {}

        # Check if key or password is provided
        if self.key_string:
            connect_kwargs["pkey"] = self._parse_private_key(self.key_string)
        elif self.key_file:
            connect_kwargs["key_filename"] = self.key_file
        elif self.password:
            connect_kwargs["password"] = self.password
        else:
            raise ValueError("Either key_file, key_string, or password must be provided for authentication.")

        # Init the connection
        self.connection = Connection(host=self.host, user=self.user, connect_kwargs=connect_kwargs)

    def _parse_private_key(self, key_string: str) -> paramiko.PKey:
        return paramiko.RSAKey.from_private_key(io.StringIO(key_string))

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

    def exists_with_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if a file or directory exists within the path that matches the pattern.

        :param path: The path to check.
        :param pattern: The pattern to match.

        :return: True if the file or directory exists and matches the pattern, False otherwise.
        """
        result = self.connection.run(f"find {path} -maxdepth 1 -name '{pattern}'", hide=True)
        # If output is non-empty, files exist
        return bool(result.stdout.strip())

    def make_dirs(self, path: str):
        """
        Create a directory.

        :param path: The path of the directory to create.
        """
        self.connection.run(f"mkdir -p {path}", hide=True)

    def write_file(self, path: str, content: str):
        """
        Write content to a file.

        :param path: The path of the file to write.
        :param content: The content to write to the file.
        """
        # self.connection.run(f'echo "{content}" > {path}', hide=True)
        self.connection.run(f"cat <<'EOF' > {path}\n{content}\nEOF", hide=True)

    def read_file(self, path: str) -> str:
        """
        Read the contents of a file.

        :param path: The path of the file to read.
        :return: The contents of the file.
        """
        result = self.connection.run(f"cat {path}", hide=True)
        return result.stdout.strip()

    def chmod(self, path: str, permissions: str):
        """
        Set the permissions of a file or directory.

        :param path: The path of the file or directory.
        :param permissions: The permissions to set.
        """
        self.connection.run(f"chmod {permissions} {path}", hide=True)

    def check_slurm_job_status(self, job_name: str, user_name: str = None) -> str:
        """
        Check the status of a SLURM job.
        :param job_name: The name of the job to check.
        :param user_name: The username of the user who submitted the job.

        :return: The status of the job, which can be 'running' if the job is currently running,
                 'queued' if the job is pending in the queue, or `None` if the job is not found.
        """

        # Run the squeue command and capture the output
        command = f'squeue -u {user_name} --format="%.8i %.7P %.80j %.8u %.2t %.10M %.6D %R"'
        result = self.connection.run(f"source /etc/profile && {command}", hide=True).stdout.strip()
        lines = result.split("\n")

        # Iterate through lines to find the job
        for line in lines:
            parts = line.split()

            job_nm, job_status = parts[2], parts[4]
            if job_nm == job_name:
                if job_status in ["R", "CG"]:  # Running or Completing
                    return "RUNNING"
                elif job_status in ["PD"]:  # Pending (queued)
                    return "QUEUED"

        return None

    def walk(self, top: str):
        """
        Generate the file names in a directory tree by walking the tree over SSH.

        :param top: The root directory to start walking from.
        :yield: A 3-tuple (dirpath, dirnames, filenames)
        """
        stack = [top]

        while stack:
            current_dir = stack.pop()
            dirnames = []
            filenames = []

            try:
                entries = self.list_directory_objects(current_dir)
            except UnexpectedExit:
                continue  # Skip directories that can't be listed

            for entry in entries:
                if entry.name in (".", ".."):
                    continue

                full_path = f"{current_dir.rstrip('/')}/{entry.name}"
                if entry.type == FileType.FOLDER:
                    dirnames.append(entry.name)
                    stack.append(full_path)
                elif entry.type == FileType.FILE:
                    filenames.append(entry.name)
                elif entry.type == FileType.LINK:
                    filenames.append(entry.name)

            yield current_dir, dirnames, filenames

    def symlink(self, target: str, link_name: str):
        """
        Create a symbolic link.

        :param target: The target file or directory.
        :param link_name: The name of the symbolic link to create.
        """
        self.connection.run(f"ln -sfn {target} {link_name}", hide=True)
