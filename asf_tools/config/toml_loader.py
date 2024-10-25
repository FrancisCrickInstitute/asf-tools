"""
Load from toml file either in a specified file path or from the default home directory.
"""

import os

import toml


def load_toml_file(file_path: str = None, file_name="crick.toml") -> dict:
    """
    Load a TOML file from a specified file path or default to a file name in the user's home directory.

    Args:
        file_path (str, optional): The full path to the TOML file. Defaults to None.
        file_name (str, optional): The name of the TOML file to load from the user's home directory if
        file_path is not provided. Defaults to "crick.toml".

    Returns:
        dict: The contents of the TOML file as a dictionary.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        toml.TomlDecodeError: If the file is not a valid TOML file.
    """

    # construct the file path
    resolved_path = file_path
    if not resolved_path:
        home_dir = os.path.expanduser("~")
        resolved_path = os.path.join(home_dir, file_name)

    # load the toml file
    with open(file_path, "r", encoding="UTF-8") as file:
        return toml.load(file)
