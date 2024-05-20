"""
Function class for managing CLI operation
"""

import os
import logging

from asf_tools.io.utils import list_directory_names
from asf_tools.nextflow.utils import create_sbatch_header

log = logging.getLogger(__name__)

NANOPORE_DEMUX_PIPELINE_VERSION = "main"


class OntGenDemuxRun():
    """
    Generates a run folder for the deumux pipeline and associated support files
    including a run script and default samplesheet
    """

    def __init__(self, source_dir, target_dir, pipeline_dir, nextflow_cache, nextflow_work, container_cache, execute) -> None:
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.pipeline_dir = pipeline_dir
        self.nextflow_cache = nextflow_cache
        self.nextflow_work = nextflow_work
        self.container_cache = container_cache
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

        return 0

    def process_run(self, run_name):
        """
        Per run processing
        """

        log.info(f"Processing: {run_name}")

        # Create folder
        folder_path = os.path.join(self.target_dir, run_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Generate and write sbatch script
        sbatch_script = self.create_sbatch_text(run_name)
        sbatch_script_path = os.path.join(folder_path, "run_script.sh")
        with open(sbatch_script_path, "w", encoding="UTF-8") as file:
            file.write(sbatch_script)

        # Write samplesheet
        samplesheet_path = os.path.join(folder_path, "samplesheet.csv")
        with open(samplesheet_path, "w", encoding="UTF-8") as file:
            file.write("sample_id,group,user,project_id,barcode\n")
            file.write("sample_01,asf,no.name,DN45678,unclassified\n")

    def create_sbatch_text(self, run_name) -> str:
        """Creates an sbatch script from a template and returns the text

        Returns:
            str: Script as a string
        """

        # Create sbatch header
        header_str = create_sbatch_header()

        # Create the bash script template with placeholders
        bash_script = header_str + f"""
#SBATCH --partition=cpu
#SBATCH --job-name=asf_nanopore_demux
#SBATCH --mem=4G
#SBATCH -n 1
#SBATCH --time=24:00:00
#SBATCH --output=run.o
#SBATCH --error=run.o

export NXF_HOME="{self.nextflow_cache}"
export NXF_WORK="{self.nextflow_work}"
export NXF_SINGULARITY_CACHEDIR="{self.container_cache}"

nextflow run {self.pipeline_dir} \\
  -profile crick \\
  -r {NANOPORE_DEMUX_PIPELINE_VERSION} \\
  --samplesheet ./samplesheet.csv \\
  --run_dir {os.path.join(self.source_dir, run_name)}
"""
        return bash_script
