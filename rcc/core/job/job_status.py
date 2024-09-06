from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class TaskStatus:
    id: str
    name: str
    state: str


@dataclass
class BaseJobStatus(ABC):
    id: str
    name: str
    state: str
    tasks: List[TaskStatus]

    @classmethod
    @abstractmethod
    def empty(cls) -> "BaseJobStatus":
        pass

    @classmethod
    @abstractmethod
    def from_output(cls, output: List[str]) -> "BaseJobStatus":
        pass

    @property
    @abstractmethod
    def is_pending(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_completed(self) -> bool:
        pass

    @property
    @abstractmethod
    def success(self) -> bool:
        pass
