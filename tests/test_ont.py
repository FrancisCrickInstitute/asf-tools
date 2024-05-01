"""
Tests covering the ont module
"""

import unittest


class TestOnt(unittest.TestCase):
    """Class for ont tests"""

    from .ont.ont_gen_demux_run import(
        test_folder_creation,
        test_sbatch_file,
        test_samplesheet_file
    )
