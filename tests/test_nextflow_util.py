"""
Tests for nextflow util functions
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

from assertpy import assert_that

from asf_tools.nextflow.utils import NEXTFLOW_VERSION, SINGULARITY_VERSION, create_sbatch_header


class TestNextflowUtils:
    """Class for testing nextflow utils"""

    def test_create_sbatch_header(self):
        """Test create sbatch header"""

        # Test
        header_str = create_sbatch_header()

        # Assert
        assert_that(header_str).contains(f"ml Nextflow/{NEXTFLOW_VERSION}")
        assert_that(header_str).contains(f"ml Singularity/{SINGULARITY_VERSION}")

    def test_create_sbatch_header_withversion(self):
        """Test create sbatch header with version"""

        # Test
        header_str = create_sbatch_header("1.0")

        # Assert
        assert_that(header_str).contains("ml Nextflow/1.0")
        assert_that(header_str).contains(f"ml Singularity/{SINGULARITY_VERSION}")
