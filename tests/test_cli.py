"""
Primary CLI Tests
"""

import tempfile
import unittest
from unittest import mock

from click.testing import CliRunner

import asf_tools.__main__


TEST_ONT_RUN_SOURCE_PATH = "tests/data/ont/runs"
TEST_ONT_PIPELINE_PATH = "tests/data/ont/nanopore_demux_pipeline"
TEST_DELIVERY_SOURCE_PATH = "tests/data/ont/live_runs/pipeline_output"


class TestCli(unittest.TestCase):
    """Class for testing the command line interface"""

    def setUp(self):
        self.runner = CliRunner()
        self.tmp_dir = tempfile.mkdtemp()

    def assemble_params(self, params):
        """Assemble a dictionary of parameters into a list of arguments for the cli"""

        arg_list = []
        for key, value in params.items():
            if value is not None:
                arg_list += [f"--{key}", value]
            else:
                arg_list += [f"--{key}"]

        return arg_list

    def invoke_cli(self, cmd):
        """Invoke the command line interface using a list of parameters"""

        return self.runner.invoke(asf_tools.__main__.asf_tools_cli, cmd)

    def test_cli_command_help(self):
        """Test the main launch function with --help"""

        result = self.invoke_cli(["--help"])

        assert result.exit_code == 0
        assert "Show this message and exit." in result.output

    def test_cli_command_incorrect(self):
        """Test the main launch function with an unrecognised subcommand"""

        result = self.invoke_cli(["foo"])

        self.assertTrue(result.exit_code == 2)

    @mock.patch("asf_tools.ont.ont_gen_demux_run.OntGenDemuxRun", autospec=True)
    def test_cli_command_ont_gen_demux_run(self, mock_obj):
        """Test ont gen demux run"""

        # Init
        params = {
            "source_dir": TEST_ONT_RUN_SOURCE_PATH,
            "target_dir": ".",
            "pipeline_dir": TEST_ONT_PIPELINE_PATH,
            "nextflow_cache": "/.nextflow/",
            "container_cache": "/sing/",
            "nextflow_work": "/work/",
            "runs_dir": TEST_ONT_RUN_SOURCE_PATH,
        }

        # Test
        cmd = ["ont", "gen-demux-run"] + self.assemble_params(params)
        result = self.invoke_cli(cmd)

        # Assert
        self.assertTrue(result.exit_code == 0)
        mock_obj.assert_called_once_with(
            params["source_dir"],
            params["target_dir"],
            params["pipeline_dir"],
            params["nextflow_cache"],
            params["nextflow_work"],
            params["container_cache"],
            params["runs_dir"],
            False,
            None,
            False,
        )

    # @mock.patch("asf_tools.io.data_management.DataManagement", autospec=True)
    # def test_cli_command_deliver_to_targets(self, mock_obj):
    #     """Test selivery of data"""
    #     # Set up
    #     # Init
    #     params = {
    #         "source_dir": TEST_DELIVERY_SOURCE_PATH,
    #         "target_dir": self.tmp_dir
    #     }

    #     # Test
    #     cmd = ["deliver-to-targets"] + self.assemble_params(params)
    #     result = self.invoke_cli(cmd)

    #     # Assert
    #     # self.assertTrue(result.exit_code == 0)
    #     mock_obj.assert_called_once_with(
    #         params["source_dir"],
    #         params["target_dir"]
    #     )
