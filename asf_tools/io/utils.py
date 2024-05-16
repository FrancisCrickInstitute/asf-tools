"""
Common utility functions for file operations.
"""

import hashlib
import io
import os
import logging

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
