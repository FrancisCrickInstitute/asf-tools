"""
Function class for managing CLI operation
"""

import logging
import os
import stat

from asf_tools.api.clarity.clarity_helper_lims import ClarityHelperLims
from asf_tools.io.data_management import DataManagement
from asf_tools.io.utils import list_directory_names
from asf_tools.nextflow.utils import create_sbatch_header


log = logging.getLogger(__name__)

PERM777 = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH

PERM666 = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH


class OntGenDemuxRun:
    """
    Generates a run folder for the demux pipeline and associated support files
    including a run script and default samplesheet
    """

    def __init__(
        self,
        source_dir,
        target_dir,
        pipeline_dir,
        nextflow_cache,
        nextflow_work,
        container_cache,
        runs_dir,
        use_api,
        contains=None,
        samplesheet_only=False,
        nextflow_version=None,
    ) -> None:
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.pipeline_dir = pipeline_dir
        self.nextflow_cache = nextflow_cache
        self.nextflow_work = nextflow_work
        self.container_cache = container_cache
        self.runs_dir = runs_dir
        self.use_api = use_api
        self.contains = contains
        self.samplesheet_only = samplesheet_only
        self.nextflow_version = nextflow_version

    def run(self):
        """
        Run function
        """

        log.debug("Scanning run folder")

        # Init
        dm = DataManagement()

        # Pull list of directory names
        source_dir_names = set(list_directory_names(self.source_dir))
        target_dir_names = set(list_directory_names(self.target_dir))

        # Check for a sequencing_summary file in source directory to show that the run is completed
        completed_runs = []
        for run_name in source_dir_names:
            run_dir = os.path.join(self.source_dir, run_name)
            completed_file_exists = dm.check_ont_sequencing_run_complete(run_dir)
            if completed_file_exists:
                completed_runs.append(run_name)
            else:
                log.debug(f"Skipping {run_name}: no summary file detected, run not completed.")
        source_dir_names = set(completed_runs)
        log.info(f"Found {len(completed_runs)} completed runs")

        # Get diff
        if self.samplesheet_only is False:
            dir_diff = source_dir_names - target_dir_names
            log.info(f"Found {len(dir_diff)} new run folders")
        else:
            dir_diff = target_dir_names
            log.info(f"Found {len(dir_diff)} existing run folders")

        # Filter for contains
        if self.contains is not None:
            dir_diff = [run for run in dir_diff if self.contains in run]
            log.info(f"Found {len(dir_diff)} new run folders after filtering for {self.contains}")

        # Process runs
        for run_name in dir_diff:
            self.process_run(run_name)

        return 0

    def process_run(self, run_name: str):
        """
        Per run processing
        """

        log.info(f"Processing: {run_name}")

        # Create folder
        folder_path = os.path.join(self.target_dir, run_name)
        if self.samplesheet_only is False and not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Generate and write sbatch script
        if self.samplesheet_only is False:
            sbatch_script = self.create_sbatch_text(run_name)
            sbatch_script_path = os.path.join(folder_path, "run_script.sh")
            with open(sbatch_script_path, "w", encoding="UTF-8") as file:
                file.write(sbatch_script)
            # Set 777 for the run script
            os.chmod(sbatch_script_path, PERM777)

        # Samplesheet path
        samplesheet_path = os.path.join(folder_path, "samplesheet.csv")

        if self.use_api is False:
            # Write default samplesheet
            with open(samplesheet_path, "w", encoding="UTF-8") as file:
                file.write("id,sample_name,group,user,project_id,barcode\n")
                file.write("sample_01,sample_01,asf,no_name,no_proj,unclassified\n")
        if self.use_api is True:
            # Get samplesheet from API
            api = ClarityHelperLims()
            sample_dict = api.collect_ont_samplesheet_info(run_name)

            # Write samplesheet
            with open(samplesheet_path, "w", encoding="UTF-8") as file:
                file.write("id,sample_name,group,user,project_id,barcode\n")
                for key, value in sample_dict.items():
                    barcode = "unclassified"
                    if "barcode" in value:
                        barcode = value["barcode"]
                    file.write(f"{key},{value['sample_name']},{value['group']},{value['user']},{value['project_id']},{barcode}\n")

        # Set 666 for the samplesheet
        os.chmod(samplesheet_path, PERM666)

    def create_sbatch_text(self, run_name) -> str:
        """Creates an sbatch script from a template and returns the text

        Returns:
            str: Script as a string
        """

        # Create sbatch header
        header_str = create_sbatch_header(self.nextflow_version)

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
#SBATCH --time=168:00:00
#SBATCH --output=run.o
#SBATCH --error=run.o
#SBATCH --res=asf

{header_str}

{nxf_home}
export NXF_WORK="{self.nextflow_work}"
export NXF_SINGULARITY_CACHEDIR="{self.container_cache}"

nextflow run {self.pipeline_dir} \\
  -resume \\
  -profile crick,nemo \\
  --monochrome_logs \\
  --samplesheet ./samplesheet.csv \\
  --run_dir {os.path.join(self.runs_dir, run_name)} \\
  --dorado_bc_parse_pos 2
"""
        return bash_script
