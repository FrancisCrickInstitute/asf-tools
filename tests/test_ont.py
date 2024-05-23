"""
Tests covering the ont module
"""

import unittest


class TestOnt(unittest.TestCase):
    """Class for ont tests"""

    from .ont.ont_gen_demux_run import (  # type: ignore[misc]  # pylint: disable=C0415
        test_file_permissions, test_folder_creation, test_samplesheet_file,
        test_sbatch_file, test_sbatch_file_nonfhome)
