"""
Function class for managing CLI operation
"""

import logging

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

        log.debug("HERE")


    # Inputs:
# Source/target set of run folders
# Identify list of folder mismatches
# for each target folder
## Generate sbatch run file
## Generate default sample sheet
## Option to actually submit the sbatch command