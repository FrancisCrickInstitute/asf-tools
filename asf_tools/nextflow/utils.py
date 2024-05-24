"""
Common utility functions for nextflow
"""

NEXTFLOW_VERSION = "23.10.0"
SINGULARITY_VERSION = "3.6.4"


def create_sbatch_header() -> str:
    """Creates a nextflow run header

    Returns:
        str: Structured header string.
    """

    header = f"""ml purge
ml Nextflow/{NEXTFLOW_VERSION}
ml Singularity/{SINGULARITY_VERSION}
"""

    return header
