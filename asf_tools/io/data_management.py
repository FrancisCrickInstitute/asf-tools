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
        # collect all sub dirs
        source_paths_list = []
        for root, dirs, files in os.walk(data_path):
            if not dirs:
                source_paths_list.append(root)
        # print(source_paths_list)

        # split paths
        folder_strucure_info = []
        for path in source_paths_list:
            relative_path = os.path.relpath(path, data_path)
            split_path = relative_path.split(os.sep)
            if len(split_path) == 4:
                group, user, projectID, runID = split_path
                info_dict = {
                    "group": group,
                    "user": user,
                    "project_ID": projectID,
                    "run_ID": runID
                }
                folder_strucure_info.append(info_dict)

        print(folder_strucure_info)        




# source_path = /path/to/results
# target_base_path = /path/to/target
# permission_depth = 2

# source_path_list = [
# /path/to/results/group_1/user_1/proj_1/run_id,
# /path/to/results/group_2/user_2/proj_2/run_id,
# /path/to/results/group_3/user_3/proj_3/run_id
# ]

# target_path_list = source_path_list.copy()
# for path in target_path_list:
#     target_path_list[i] = target_path_list[i].replace(source_path, "")
#     target_path_list[i] = os.path.join(basepath, target_path_list[i])


# other_list [
#     group_1/user_1/proj_1/run_id
#     group_1/user_1/proj_1/run_id
#     group_1/user_1/proj_1/run_id
#     group_1/user_1/proj_1/run_id
# ]

# for target in other_list:
#     t_split = target.split("/")
#     t_depth = t_split[:2]
#     t_depth //  group_1/user_1
#     check_path = os.join(target_base_path, t_depth)

#     // check if path exists

# // go through target_path_list - depth -1
# // mkdir

# // symlink to target
