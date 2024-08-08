"""
Common utility functions for nextflow
"""

NEXTFLOW_VERSION = "24.04.2"
SINGULARITY_VERSION = "3.6.4"


def create_sbatch_header(nextflow_version: str = None) -> str:
    """Creates a nextflow run header

    Returns:
        str: Structured header string.
    """
    nf_version = NEXTFLOW_VERSION if nextflow_version is None else nextflow_version

    header = f"""ml purge
ml Nextflow/{nf_version}
ml Singularity/{SINGULARITY_VERSION}
"""

    return header
