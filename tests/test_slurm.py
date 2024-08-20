"""
Tests covering the slurm module
"""

import unittest


class TestOnt(unittest.TestCase):
    """Class for ont tests"""

    from .slurm.utils import (  # type: ignore[misc]  # pylint: disable=C0415
        test_get_job_status_report_from_file,
        test_get_job_status_report_notexist,
        test_get_job_status_report_queued,
        test_get_job_status_report_running,
    )
