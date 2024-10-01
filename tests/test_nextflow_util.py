"""
Tests for nextflow util functions
"""

import unittest

from asf_tools.nextflow.utils import NEXTFLOW_VERSION, SINGULARITY_VERSION, create_sbatch_header

class TestNextflowUtils(unittest.TestCase):
    """Class for testing nextflow utils"""

    def test_create_sbatch_header(self):
        """Test create sbatch header"""

        # Test
        header_str = create_sbatch_header()

        # Assert
        self.assertTrue(f"ml Nextflow/{NEXTFLOW_VERSION}" in header_str)
        self.assertTrue(f"ml Singularity/{SINGULARITY_VERSION}" in header_str)


    def test_create_sbatch_header_withversion(self):
        """Test create sbatch header with version"""

        # Test
        header_str = create_sbatch_header("1.0")

        # Assert
        self.assertTrue("ml Nextflow/1.0" in header_str)
        self.assertTrue(f"ml Singularity/{SINGULARITY_VERSION}" in header_str)
