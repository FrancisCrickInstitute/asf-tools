"""
Helper functions for data management
"""

# import os
# import pandas as pd

class DataTransfer:
    """
    Creates symlinks from raw data to scientist folder
    """

    def transfer_data(self, data_path: str, symlink_data_path: str):
        pass
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