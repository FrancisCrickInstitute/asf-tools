"""
Tests for ssh FileObject.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,invalid-name

import unittest
from datetime import datetime
from asf_tools.ssh.file_object import FileObject, FileType


class TestSshFileObject(unittest.TestCase):

    def test_ssh_file_object_initialization(self):
        file_obj = FileObject(
            permissions="-rw-r--r--",
            owner="user",
            group="group",
            size="1234",
            last_modified="2023-10-01 12:34",
            name="test_file.txt"
        )
        self.assertEqual(file_obj.name, "test_file.txt")
        self.assertEqual(file_obj.owner, "user")
        self.assertEqual(file_obj.group, "group")
        self.assertEqual(file_obj.size, 1234)
        self.assertEqual(file_obj.last_modified, datetime(2023, 10, 1, 12, 34))
        self.assertEqual(file_obj.type, FileType.FILE)
        self.assertEqual(file_obj.permissions, {
            'user': ['read', 'write', 'none'],
            'group': ['read', 'none', 'none'],
            'others': ['read', 'none', 'none']
        })

    def test_ssh_file_object_link(self):
        file_obj = FileObject(
            permissions="lrwxrwxrwx",
            owner="user",
            group="group",
            size="1234",
            last_modified="2023-10-01 12:34",
            name="link -> target"
        )
        self.assertEqual(file_obj.name, "link")
        self.assertEqual(file_obj.link_target, "target")
        self.assertEqual(file_obj.type, FileType.LINK)

    def test_ssh_file_object_folder(self):
        file_obj = FileObject(
            permissions="drwxr-xr-x",
            owner="user",
            group="group",
            size="4096",
            last_modified="2023-10-01 12:34",
            name="test_folder"
        )
        self.assertEqual(file_obj.type, FileType.FOLDER)
