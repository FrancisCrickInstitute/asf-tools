"""
Tests for io util functions
"""

import os

from asf_tools.io.utils import list_directory_names

from ..utils import with_temporary_folder


def test_list_directory(self):
    """Test list directories"""

    # Setup
    path = "tests/data/ont/runs"

    # Test
    dir_list = list_directory_names(path)

    # Assert
    self.assertEqual(len(dir_list), 3)


@with_temporary_folder
def test_list_directory_symlink(self, tmp_path):
    """Test list directories"""

    # Setup
    path = "tests/data/ont/runs"

    # Create symlinks
    for entry in os.listdir(path):
        source_path = os.path.join(path, entry)
        if os.path.isdir(source_path):
            symlink_path = os.path.join(tmp_path, entry)
            os.symlink(source_path, symlink_path)

    # Test
    dir_list = list_directory_names(tmp_path)

    # Assert
    self.assertEqual(len(dir_list), 3)
