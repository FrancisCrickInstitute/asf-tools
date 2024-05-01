"""
Tests for nextflow util functions
"""

from asf_tools.nextflow.utils import create_sbatch_header, NEXTFLOW_VERSION, SINGULARITY_VERSION


def test_create_sbatch_header(self):
    """Test create sbatch header"""

    # Test
    header_str = create_sbatch_header()

    # Assert
    self.assertTrue(f"ml Nextflow/{NEXTFLOW_VERSION}" in header_str)
    self.assertTrue(f"ml Singularity/{SINGULARITY_VERSION}" in header_str)
