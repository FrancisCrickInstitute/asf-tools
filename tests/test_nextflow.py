"""
Tests covering the nextflow module
"""

import unittest


class TestNextflow(unittest.TestCase):
    """Class for nextflow tests"""

    from .nextflow.util import (  # type: ignore[misc]  # pylint: disable=C0415
        test_create_sbatch_header
    )
