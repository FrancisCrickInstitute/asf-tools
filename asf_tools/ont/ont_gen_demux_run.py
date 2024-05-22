"""
Function class for managing CLI operation
"""

import os
import logging
import stat

from asf_tools.io.utils import list_directory_names
from asf_tools.nextflow.utils import create_sbatch_header

log = logging.getLogger(__name__)

PERM777 = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | \
    stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | \
    stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH

PERM666 = stat.S_IRUSR | stat.S_IWUSR | \
    stat.S_IRGRP | stat.S_IWGRP | \
    stat.S_IROTH | stat.S_IWOTH


class OntGenDemuxRun():
    """
    Generates a run folder for the deumux pipeline and associated support files
    including a run script and default samplesheet
    """

    def __init__(self, source_dir, target_dir, pipeline_dir, nextflow_cache, nextflow_work, container_cache, runs_dir, execute) -> None:
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.pipeline_dir = pipeline_dir
        self.nextflow_cache = nextflow_cache
        self.nextflow_work = nextflow_work
        self.container_cache = container_cache
        self.runs_dir = runs_dir
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
            file.write("sample_01,asf,no_name,no_proj,unclassified\n")

        # Set 777 for the run script
        os.chmod(sbatch_script_path, PERM777)

        # Set 666 for the samplesheet
        os.chmod(samplesheet_path, PERM666)

    def create_sbatch_text(self, run_name) -> str:
        """Creates an sbatch script from a template and returns the text

        Returns:
            str: Script as a string
        """

        # Create sbatch header
        header_str = create_sbatch_header()

        # Create NXF_HOME string
        nxf_home = ""
        if self.nextflow_cache != "":
            nxf_home = f'export NXF_HOME="{self.nextflow_cache}"'

        # Create the bash script template with placeholders
        bash_script = f"""#!/bin/sh

#SBATCH --partition=ncpu
#SBATCH --job-name=asf_nanopore_demux_{run_name}
#SBATCH --mem=4G
#SBATCH -n 1
#SBATCH --time=72:00:00
#SBATCH --output=run.o
#SBATCH --error=run.o

{header_str}

{nxf_home}
export NXF_WORK="{self.nextflow_work}"
export NXF_SINGULARITY_CACHEDIR="{self.container_cache}"

nextflow run {self.pipeline_dir} \\
  -profile crick,nemo \\
  --monochrome_logs \\
  --samplesheet ./samplesheet.csv \\
  --run_dir {os.path.join(self.runs_dir, run_name)}
"""
        return bash_script
