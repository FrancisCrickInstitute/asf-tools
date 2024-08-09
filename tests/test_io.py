"""
Tests covering the io module
"""

import unittest


class TestIo(unittest.TestCase):
    """Class for io tests"""

    from .io.utils import test_list_directory, test_list_directory_symlink  # type: ignore[misc]  # pylint: disable=C0415

    from .io.data_management import (  # type: ignore[misc]  # pylint: disable=C0415
        test_symlink_to_target_isinvalid_source,
        test_symlink_to_target_isinvalid_target,
        test_symlink_to_target_isvalid_str,
        test_symlink_to_target_isvalid_list,
        test_deliver_to_targets_valid,
        test_deliver_to_targets_no_user,
        test_deliver_to_targets_source_invalid,
    )
