"""
Common utility functions for nextflow
"""

NEXTFLOW_VERSION = "23.10.0"
SINGULARITY_VERSION = "3.6.4"


def create_sbatch_header():
    """Creates a nextflow run header"""

    header = f"""
        #!/bin/sh

        ml purge
        ml Nextflow/{NEXTFLOW_VERSION}
        ml Singularity/{SINGULARITY_VERSION}
        """

    return header
