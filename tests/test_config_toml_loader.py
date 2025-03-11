"""
Tests for the toml_loader module.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring

import os
from assertpy import assert_that
from unittest.mock import mock_open, patch

import toml

from asf_tools.config.toml_loader import load_toml_file


class TestTomlLoader():

    def test_load_toml_file_with_file_path(self):
        mock_data = {"key": "value"}
        with patch("builtins.open", mock_open(read_data=toml.dumps(mock_data))):
            assert_that(load_toml_file(file_path="/path/to/file.toml")).is_equal_to(mock_data)

    def test_load_toml_file_with_file_name(self):
        mock_data = {"key": "value"}
        home_dir = os.path.expanduser("~")
        # file_path = os.path.join(home_dir, "crick.toml")
        with patch("builtins.open", mock_open(read_data=toml.dumps(mock_data))):
            with patch("os.path.expanduser", return_value=home_dir):
                assert_that(load_toml_file()).is_equal_to(mock_data)

    def test_load_toml_file_with_invalid_toml(self):
        invalid_toml_data = "invalid_toml"
        with patch("builtins.open", mock_open(read_data=invalid_toml_data)):
            assert_that(load_toml_file).raises(toml.TomlDecodeError).when_called_with(file_path="/path/to/invalid.toml")

    def test_load_toml_file_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert_that(load_toml_file).raises(FileNotFoundError).when_called_with(file_path="/path/to/nonexistent.toml")
