"""
Tests covering the nextflow module
"""

import unittest


class TestNextflow(unittest.TestCase):
    """Class for nextflow tests"""

    from .nextflow.gen_demux_run import (  # type: ignore[misc]  # pylint: disable=C0415
        test_create_sbatch_with_parse_pos,
        test_create_sbatch_without_parse_pos,
        test_ont_gen_demux_run_file_permissions,
        test_ont_gen_demux_run_folder_creation_isvalid,
        test_ont_gen_demux_run_folder_creation_with_contains,
        test_ont_gen_demux_run_samplesheet_file_noapi,
        test_ont_gen_demux_run_sbatch_file,
        test_ont_gen_demux_run_sbatch_file_nonfhome,
        test_ont_gen_demux_samplesheet_multi_sample,
        test_ont_gen_demux_samplesheet_only,
        test_ont_gen_demux_samplesheet_single_sample,
    )
    from .nextflow.util import test_create_sbatch_header, test_create_sbatch_header_withversion  # type: ignore[misc]  # pylint: disable=C0415
