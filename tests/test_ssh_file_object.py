"""
Tests for ssh FileObject.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,invalid-name

from datetime import datetime

from assertpy import assert_that

from asf_tools.ssh.file_object import FileObject, FileType


class TestSshFileObject:

    def test_ssh_file_object_initialization(self):
        file_obj = FileObject(
            permissions="-rw-r--r--", owner="user", group="group", size="1234", last_modified="2023-10-01 12:34", name="test_file.txt"
        )
        assert_that(file_obj.name).is_equal_to("test_file.txt")
        assert_that(file_obj.owner).is_equal_to("user")
        assert_that(file_obj.group).is_equal_to("group")
        assert_that(file_obj.size).is_equal_to(1234)
        assert_that(file_obj.last_modified).is_equal_to(datetime(2023, 10, 1, 12, 34))
        assert_that(file_obj.type).is_equal_to(FileType.FILE)
        assert_that(file_obj.permissions).is_equal_to(
            {"user": ["read", "write", "none"], "group": ["read", "none", "none"], "others": ["read", "none", "none"]}
        )

    def test_ssh_file_object_link(self):
        file_obj = FileObject(
            permissions="lrwxrwxrwx", owner="user", group="group", size="1234", last_modified="2023-10-01 12:34", name="link -> target"
        )
        assert_that(file_obj.name).is_equal_to("link")
        assert_that(file_obj.link_target).is_equal_to("target")
        assert_that(file_obj.type).is_equal_to(FileType.LINK)

    def test_ssh_file_object_folder(self):
        file_obj = FileObject(
            permissions="drwxr-xr-x", owner="user", group="group", size="4096", last_modified="2023-10-01 12:34", name="test_folder"
        )
        assert_that(file_obj.type).is_equal_to(FileType.FOLDER)
