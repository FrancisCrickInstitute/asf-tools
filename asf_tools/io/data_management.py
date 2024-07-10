"""
Helper functions for data management
"""

import os

# import pandas as pd
import subprocess


class DataManagement:
    """
    Creates symlinks from raw data to symlink_folder
    """

    def data_management(self, data_path: str, symlink_data_path):
        """
        Creates symbolic links for a given data path in one or multiple destination paths.

        Args:
        - data_path (str): Path to the source data to be symlinked.
        - symlink_data_path (Union[str, list]): Single path or list of paths where the symlinks should be created.

        Raises:
        - ValueError: If symlink_data_path is neither a string nor a list.
        - subprocess.CalledProcessError: If the subprocess command fails.

        Example usage:
        transfer_data('/path/to/source', '/path/to/destination')
        transfer_data('/path/to/source', ['/path/to/dest1', '/path/to/dest2'])
        """

        # Check if source paths exists
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"{data_path} does not exist.")

        # Check if it's a single or multiple target paths
        if isinstance(symlink_data_path, str):
            # Check if target path exists
            if not os.path.exists(symlink_data_path):
                raise FileNotFoundError(f"{symlink_data_path} does not exist.")

            cmd = f"ln -sfn {data_path} {symlink_data_path}"
            subprocess.run(cmd, shell=True, check=True)

        elif isinstance(symlink_data_path, list):
            for item in symlink_data_path:
                # Check if target paths exists
                if not os.path.exists(item):
                    raise FileNotFoundError(f"{item} does not exist.")

                cmd = f"ln -sfn {data_path} {item}"
                subprocess.run(cmd, shell=True, check=True)
        else:
            raise ValueError("symlink_data_path must be either a string or a list of strings")
