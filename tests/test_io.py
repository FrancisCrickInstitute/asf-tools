"""
Tests covering the io module
"""

import unittest


class TestIo(unittest.TestCase):
    """Class for io tests"""

    from .io.data_management import (  # type: ignore[misc]  # pylint: disable=C0415
        test_check_pipeline_run_complete_false,
        test_check_pipeline_run_complete_true,
        test_check_ont_sequencing_run_complete_false,
        test_check_ont_sequencing_run_complete_true,
        test_deliver_to_targets_no_user,
        test_deliver_to_targets_source_invalid,
        test_deliver_to_targets_symlink_overide,
        test_deliver_to_targets_valid,
        test_scan_delivery_state_all_to_deliver,
        test_scan_delivery_state_none_to_deliver,
        test_scan_delivery_state_partial_to_deliver,
        test_scan_delivery_state_source_invalid,
        test_scan_delivery_state_target_invalid,
        test_symlink_to_target_isinvalid_target,
        test_symlink_to_target_isvalid_list,
        test_symlink_to_target_isvalid_str,
    )
    from .io.utils import (  # type: ignore[misc]  # pylint: disable=C0415
        test_check_file_exist_invalid,
        test_check_file_exist_isvalid,
        test_check_file_exist_pathnotexist,
        test_list_directory,
        test_list_directory_symlink,
    )
