"""
Function class for managing CLI operation
"""

import os
import logging

from asf_tools.io.utils import list_directory_names

log = logging.getLogger(__name__)


class OntGenDemuxRun():
    """
    Generates a run folder for the deumux pipeline and associated support files
    including a run script and default samplesheet
    """

    def __init__(self, source_dir, target_dir, execute) -> None:
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.execute = execute

    def run(self):
        """
        Run function
        """

        log.debug("Scanning run folder")

        # Pull list of directory names
        source_dir_names = set(list_directory_names(self.source_dir))
        target_dir_names = set(list_directory_names(self.target_dir))

        # Get diff
        dir_diff = source_dir_names - target_dir_names
        log.info(f"Found {len(dir_diff)} new run folders")

        # Process runs
        for run_name in dir_diff:
            self.process_run(run_name)

    def process_run(self, run_name):
        """
        Per run processing
        """

        log.info(f"Processing: {run_name}")

        # Create folder
        folder_path = os.path.join(self.target_dir, run_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def create_sbatch_text(self):
        """
        Creates an sbatch script from a template and returns the text
        """

        # Create the bash script template with placeholders
        bash_script = f"""
        #!/bin/bash
        # Pipeline script
        {pipeline_step1}
        {pipeline_step2}
        """




## Generate sbatch run file
## Generate default sample sheet
## Option to actually submit the sbatch command