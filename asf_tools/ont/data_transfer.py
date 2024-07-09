"""
Helper functions for data management
"""

import os
# import pandas as pd
import subprocess

class DataTransfer:
    """
    Creates symlinks from raw data to scientist folder
    """

    def data_transfer(self, data_path: str, symlink_data_path):
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

            # Simlink data
            cmd = f"ln -sfn {data_path} {symlink_data_path}" #apparently ln -sn is incorrect
            subprocess.run(cmd, shell=True, check=True)
            content_temp_folder = f"ls {symlink_data_path}"
            subprocess.run(content_temp_folder, shell=True, check=True)

        elif isinstance(symlink_data_path, list):
            for item in symlink_data_path:
                # Check if target paths exists
                if not os.path.exists(item):
                    raise FileNotFoundError(f"{item} does not exist.")
                # Simlink data
                cmd = f"ln -sfn {data_path} {item}"
                subprocess.run(cmd, shell=True, check=True)
        else:
            raise ValueError("symlink_data_path must be either a string or a list of strings")


    # check if data_path and symlink_data_path exist
    #set up default values for data_path + symlink_data_path


    ### for future use ###
    # uses samplesheet to build the target dir (ie. where data is shared with the users)
    # not completed and not tested
    #
    # def target_path_build(self, samplesheet):
    #     # Extract relevant values from the samplesheet for building delivery path
    #     samplesheet_dict = {}
    #     df = pd.read_csv(samplesheet)
    #     columns_to_include = ['group', 'user', 'project_id']
    #     for index, row in df.iterrows():
    #         key = row["sample_id"]
    #         row_dict = {col: row[col] for col in columns_to_include}
    #         samplesheet_dict[key] = row_dict
    #     runID = os.path.basename(data_path)

    #     # build delivery path for each 
    #     for key in samplesheet_dict:


    #     symlink_data_full_path = os.path.join(symlink_data_path, group, user, project_id, runID)
    #     cmd = f'ln -s {data_path} {symlink_data_full_path}'



# check samplesheet 
#   if user or group missing -> raise warning or error

# include situation where target dir does not exist -> only root users can create a new folder
#   if folder doesn't exist -> raise warning or error