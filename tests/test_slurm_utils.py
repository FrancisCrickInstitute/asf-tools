"""
Test the Slurm utils
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

from unittest.mock import MagicMock, patch

from assertpy import assert_that

from asf_tools.slurm.utils import get_job_status


class TestSlurmUtils:
    """Class for testing Slurm utils"""

    @patch("asf_tools.slurm.utils.subprocess.run")
    def test_get_job_status_report_notexist(self, mock_run):
        """
        Test the get_job_status function when the job is queued
        """
        with open("tests/data/slurm/squeue/job_report_queued.txt", "r", encoding="UTF-8") as file:
            mock_output = file.read()

        # Set up the mock to return this output
        mock_run.return_value = MagicMock(stdout=mock_output)

        # Test for a running job
        status = get_job_status("test", "svc-asf-seq")

        assert_that(status).is_none()

    @patch("asf_tools.slurm.utils.subprocess.run")
    def test_get_job_status_report_running(self, mock_run):
        """
        Test the get_job_status function when the job is running
        """
        with open("tests/data/slurm/squeue/job_report_running.txt", "r", encoding="UTF-8") as file:
            mock_output = file.read()

        # Set up the mock to return this output
        mock_run.return_value = MagicMock(stdout=mock_output)

        # Test for a running job
        status = get_job_status("asf_nanopore_demux_20240717_1730_1A_PAW36768_7b0e525", "svc-asf-seq")

        assert_that(status).is_equal_to("running")

    @patch("asf_tools.slurm.utils.subprocess.run")
    def test_get_job_status_report_queued(self, mock_run):
        """
        Test the get_job_status function when the job is queued
        """
        with open("tests/data/slurm/squeue/job_report_queued.txt", "r", encoding="UTF-8") as file:
            mock_output = file.read()

        # Set up the mock to return this output
        mock_run.return_value = MagicMock(stdout=mock_output)

        # Test for a running job
        status = get_job_status("asf_nanopore_demux_20240717_1730_1A_PAW36768_7b0e525", "svc-asf-seq")

        assert_that(status).is_equal_to("queued")

    def test_get_job_status_report_from_file(self):
        """
        Test the get_job_status function when the job is queued
        """

        # Test for a running job
        status = get_job_status(
            "asf_nanopore_demux_20240717_1730_1A_PAW36768_7b0e525", "svc-asf-seq", status_file="tests/data/slurm/squeue/job_report_queued.txt"
        )

        assert_that(status).is_equal_to("queued")
