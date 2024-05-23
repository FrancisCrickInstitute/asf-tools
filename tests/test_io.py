"""
Tests covering the io module
"""

import unittest


class TestIo(unittest.TestCase):
    """Class for io tests"""

    from .io.utils import (  # type: ignore[misc]  # pylint: disable=C0415
        test_list_directory,
        test_list_directory_symlink,
    )
