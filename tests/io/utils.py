"""
Tests for io util functions
"""

from asf_tools.io.utils import list_directory_names


def test_list_directory(self):
    """Test list directories"""

    # Setup
    path = "tests/data/ont/runs"

    # Test
    dir_list = list_directory_names(path)

    # Assert
    self.assertEqual(len(dir_list), 2)
