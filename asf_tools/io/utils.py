"""
Common utility functions for file operations.
"""

import hashlib
import io
import logging
import os
import re
import shutil


log = logging.getLogger(__name__)


def file_md5(fname: str) -> str:
    """Calculates the md5sum for a file on the disk.

    Args:
        fname (str): Path to a local file.
    """

    # Calculate the md5 for the file on disk
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(io.DEFAULT_BUFFER_SIZE), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def validate_file_md5(file_name: str, expected_md5hex: str) -> bool:
    """Validates the md5 checksum of a file on disk.

    Args:
        file_name (str): Path to a local file.
        expected (str): The expected md5sum.

    Raises:
        IOError, if the md5sum does not match the remote sum.
    """
    # Make sure the expected md5 sum is a hexdigest
    try:
        int(expected_md5hex, 16)
    except ValueError as ex:
        raise ValueError(f"The supplied md5 sum must be a hexdigest but it is {expected_md5hex}") from ex

    file_md5hex = file_md5(file_name)

    if file_md5hex.upper() != expected_md5hex.upper():
        raise IOError(f"{file_name} md5 does not match remote: {expected_md5hex} - {file_md5hex}")

    return True


def list_directory_names(path: str) -> list:
    """Returns a list of directory names in the given path.

    Args:
        path (str): Path to directory to list.

    """

    directories = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)

        if os.path.isdir(full_path):
            directories.append(entry)
        elif os.path.islink(full_path) and os.path.isdir(os.readlink(full_path)):
            directories.append(entry)
        elif os.path.islink(full_path) and (not os.path.isfile(os.readlink(full_path))):  # For mounted file systems in containers
            directories.append(entry)
    return directories


def check_file_exist(path: str, pattern: str) -> bool:
    """
    Searches for a file that contains a specific pattern in its name within the top-level directory.

    Args:
    path (str): The directory path where the search should be performed.
    pattern (str): The pattern to search for within file names.

    Returns:
    bool: True if a file containing the given pattern is found, False otherwise.

    Raises:
    FileNotFoundError: If the provided path does not exist or is not a directory.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist.")

    # Search for files that match regex with error handling
    try:
        re_pattern = re.compile(pattern)
    except re.error:
        log.error(f"Invalid regex pattern: {pattern}")
        return False
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            try:
                if re_pattern.search(filename):
                    return True
            except re.error:
                return False
    return False

def delete_all_items(path: str, mode: str = "files_in_dir"):
    """
    Deletes files or directories based on the specified mode.

    Parameters:
    - path (str): The path to the file or directory to delete.
    - mode (str): The deletion mode.
    - "files_in_dir": Deletes all files within a directory but keeps the directory structure.
    - "dir_tree": Deletes the entire directory and all its contents.

    Raises:
    - ValueError: If an invalid mode is provided or if the path does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")

    if mode == "files_in_dir":
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
        else:
            raise ValueError(f"Expected a directory, but got a file: {path}")

    elif mode == "dir_tree":
        if os.path.isdir(path):
            shutil.rmtree(path)

    else:
        raise ValueError(f"Invalid mode: {mode}. Choose from 'files_in_dir', 'dir_tree'.")
