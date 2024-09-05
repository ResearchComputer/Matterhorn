import os
from matterhorn.core.filesystem import Filesystem, FilesystemFactory
from .localfs import localfilesystem
from .sshfs import sshfilesystem
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matterhorn.core.utils import Options


class PyFilesystemFactory(FilesystemFactory):
    def __init__(self, options: "Options") -> None:
        self._options = options

    def create_local_filesystem(self) -> Filesystem:
        return localfilesystem(os.getcwd())

    def create_ssh_filesystem(self) -> Filesystem:
        connection = self._options.connection
        proxyjumps = self._options.proxyjumps
        return sshfilesystem(connection, proxyjumps)
