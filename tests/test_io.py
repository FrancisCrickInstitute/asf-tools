"""
Tests covering the io module
"""

import unittest


class TestIo(unittest.TestCase):
    """Class for io tests"""

    from .io.utils import test_list_directory, test_list_directory_symlink  # type: ignore[misc]  # pylint: disable=C0415
