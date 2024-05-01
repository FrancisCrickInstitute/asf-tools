"""
Primary CLI Tests
"""

import tempfile
import unittest
from unittest import mock

from click.testing import CliRunner

import asf_tools.__main__


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

    # @mock.patch("carmack.__main__.BarcodeExtractor", autospec=True)
    # def test_cli_command_extract_cell_barcodes(self, mock_barcode_ext): 
    #     """Test extract_cell_barcodes"""

    #     # Init
    #     params = {"chemistry": "hydrop", 
    #               "max_dist": 2,
    #               "line_count": 100,
    #               "output_dir": ".",
    #               "prefix": ''}

    #     # Test
    #     cmd = ["extract-cell-barcodes"] + [R1_PATH, R2_PATH, CB_PATH] + self.assemble_params(params)
    #     result = self.invoke_cli(cmd)

    #     # Assert
    #     self.assertTrue(result.exit_code == 0)
    #     mock_barcode_ext.assert_called_once_with(R1_PATH, R2_PATH, CB_PATH, params["chemistry"]) 
    #     mock_barcode_ext.return_value.extract_cell_barcodes.assert_called_once_with(params["max_dist"], params["line_count"], params["output_dir"], params["prefix"])