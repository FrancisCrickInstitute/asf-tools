"""
Function class for managing CLI operation
"""

import logging

from asf_tools.io.data_management import DataManagement

log = logging.getLogger(__name__)

class DataManagementCli:
    """
    Symlinks data to a target path and logs the operation
    """

    def __init__(
            self,
            source_dir,
            target_dir
    ):
        self.source_dir = source_dir
        self.target_dir = target_dir

    def run(self):
        """
        Run function
        """

        log.info(f"Symlinking {self.source_dir} to {self.target_dir}")
        dt = DataManagement()
        dt.data_management(self.source_dir, self.target_dir)
