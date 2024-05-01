"""
Tests covering the nextflow module
"""

import unittest


class TestNextflow(unittest.TestCase):
    """Class for nextflow tests"""

    from .nextflow.util import test_create_sbatch_header
