import os
from matterhorn.core.filesystem import (
    Filesystem,
    localfilesystem,
    FilesystemFactory,
    PyFilesystemFactory,
    CopyInstruction,
)
from matterhorn.core.utils import Options
from matterhorn.core.executor import CommandExecutor
from matterhorn.core.ssh import SSHExecutor, ConnectionData
from matterhorn.core.ui import UI
from matterhorn.core.application import Application
from typing import Any, Dict, List, Union, cast, Optional, Protocol


class ServiceRegistry(Protocol):
    """
    A container for dependencies to be used
    """

    def local_filesystem(self) -> Filesystem:
        """
        Returns the local filesystem
        """
        ...

    def get_executor(self, options: Options) -> CommandExecutor:
        """
        Returns the CommandExecutor to be used.
        """
        ...

    def get_filesystem_factory(self, options: Options) -> FilesystemFactory:
        """
        Returns the FilesystemFactory to be used.
        """
        ...


class ProductionServiceRegistry:
    """
    The default implementation for the ServiceRegistry protocol
    """

    def local_filesystem(self) -> Filesystem:
        return localfilesystem(os.getcwd())

    def get_executor(self, options: Options) -> CommandExecutor:
        return SSHExecutor(options.connection, options.proxyjumps)

    def get_filesystem_factory(self, options: Options) -> FilesystemFactory:
        return PyFilesystemFactory(options)


def create_application(
    options: Options, service_registry: ServiceRegistry, ui: UI
) -> Application:
    executor = service_registry.get_executor(options)
    filesystem_factory = service_registry.get_filesystem_factory(options)
    return Application(executor, filesystem_factory, ui)



def proxyjumps(proxyjumps: List[Dict[str, str]]) -> List[ConnectionData]:
    return [connection_data_from_dict(proxy) for proxy in proxyjumps]


def connection_dict(
    config: Dict[str, Any]
) -> Dict[str, Union[ConnectionData, List[ConnectionData]]]:
    return {
        "connection": connection_data_from_dict(config),
        "proxyjumps": proxyjumps(config.get("proxyjumps", [])),
    }


def expand_or_none(config_entry: Optional[str]) -> Optional[str]:
    if not config_entry:
        return None

    return os.path.expandvars(config_entry)


def connection_data_from_dict(config: Dict[str, str]) -> ConnectionData:
    return ConnectionData(
        hostname=cast(str, expand_or_none(config["host"])),
        username=cast(str, expand_or_none(config["user"])),
        keyfile=expand_or_none(config.get("private_keyfile")),
        password=expand_or_none(str(config.get("password"))),
    )

def copy_instruction_from_dict(
    cp: Dict[str, Any], dest_keyname: str = "to"
) -> CopyInstruction:
    return CopyInstruction(
        os.path.expandvars(cp["from"]),
        os.path.expandvars(cp[dest_keyname]),
        bool(cp.get("overwrite", False)),
    )


def clean_instructions(clean_instructions: List[str]) -> List[str]:
    return [os.path.expandvars(ci) for ci in clean_instructions]

def connection_dict(
    config: Dict[str, Any]
) -> Dict[str, Union[ConnectionData, List[ConnectionData]]]:
    return {
        "connection": connection_data_from_dict(config),
        "proxyjumps": proxyjumps(config.get("proxyjumps", [])),
    }