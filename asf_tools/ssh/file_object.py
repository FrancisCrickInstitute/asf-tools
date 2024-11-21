"""
Represents a parsed file object from a remote connection
"""

from datetime import datetime
from enum import Enum

class FileType(Enum):
    """
    Enum for file types
    """
    FOLDER = "folder"
    FILE = "file"
    LINK = "link"
    OTHER = "other"

    def __str__(self):
        return self.value

class FileObject:
    """
    Represents a parsed file object from a remote connection
    """

    def __init__(self, permissions, owner, group, size, last_modified, name):
        self.name = name
        self.owner = owner
        self.group = group
        self.size = int(size)
        self.last_modified = datetime.strptime(last_modified, "%Y-%m-%d %H:%M")
        self.type = self._get_file_type(permissions)
        self.permissions = self._parse_permissions(permissions)

        # if link, parse the link target
        if self.type == FileType.LINK:
            self.link_target = name.split(' -> ')[1]
            self.name = self.name.split(' -> ')[0]

    def _get_file_type(self, permissions):
        if permissions.startswith('d'):
            return FileType.FOLDER
        elif permissions.startswith('-'):
            return FileType.FILE
        elif permissions.startswith('l'):
            return FileType.LINK
        else:
            return FileType.OTHER

    def _parse_permissions(self, permissions):
        permission_map = {
            'r': 'read',
            'w': 'write',
            'x': 'execute',
            '-': 'none'
        }
        parsed_permissions = {
            'user': [permission_map[perm] for perm in permissions[1:4]],
            'group': [permission_map[perm] for perm in permissions[4:7]],
            'others': [permission_map[perm] for perm in permissions[7:10]]
        }
        return parsed_permissions

    def __repr__(self):
        return (f"<type={self.type},name={self.name},owner={self.owner},group={self.group},size={self.size},last_modified={self.last_modified}>")
