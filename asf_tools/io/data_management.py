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

    def symlink_to_target(self, data_path: str, symlink_data_path):
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

    def deliver_to_targets(self, data_path: str, symlink_data_basepath: str):
        """
        Recursively collects subdirectories from `data_path`, collects info based on the path structure,
        and creates symlinks to `symlink_data_basepath`.

        Args:
            data_path (str): The base input directory containing the data to be symlinked.
            symlink_data_basepath (str): The base target directory where symlinks will be created.

        Returns:
            None
        """
        # collect all sub dirs
        source_paths_list = []
        for root, dirs, files in os.walk(data_path):
            if not dirs:
                source_paths_list.append(root)

        for path in source_paths_list:
            # split paths
            relative_path = os.path.relpath(path, data_path)
            split_path = relative_path.split(os.sep)
            if len(split_path) == 4:
                group, user, project_ID, run_ID = split_path
                info_dict = {
                    "group": group,
                    "user": user,
                    "project_ID": project_ID,
                    "run_ID": run_ID
                }

                # create project folders in target path
                permissions_path = os.path.join(symlink_data_basepath, info_dict["group"], info_dict['user'])
                if os.path.exists(permissions_path):
                    project_path = os.path.join(permissions_path, info_dict["project_ID"])
                    if not os.path.exists(project_path):
                        os.mkdir(project_path)

                # symlink data to target path
                self.symlink_to_target(path, project_path)
