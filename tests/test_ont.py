"""
Tests covering the ont module
"""

import unittest


class TestOnt(unittest.TestCase):
    """Class for ont tests"""

    from .ont.ont_gen_demux_run import (  # type: ignore[misc]  # pylint: disable=C0415
        test_ont_gen_demux_run_file_permissions,
        test_ont_gen_demux_run_folder_creation,
        test_ont_gen_demux_run_samplesheet_file,
        test_ont_gen_demux_run_sbatch_file,
        test_ont_gen_demux_run_sbatch_file_nonfhome,
        test_ont_gen_demux_run_folder_creation_with_contains
    )
