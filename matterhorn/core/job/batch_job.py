from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from .job_watcher import JobWatcherFactory, JobWatcherImpl, JobWatcher
from .job_status import BaseJobStatus

if TYPE_CHECKING:
    from matterhorn.core.controller import BaseController


class BaseBatchJob:
    def __init__(
        self,
        controller: "BaseController",
        jobid: str = "",
        watcher_factory: Optional[JobWatcherFactory] = None,
    ):
        self._controller = controller
        self._watcher_factory = watcher_factory or JobWatcherImpl
        self.jobid = jobid

    @abstractmethod
    def cancel(self) -> None:
        pass

    @abstractmethod
    def poll_status(self) -> "BaseJobStatus":
        pass

    @abstractmethod
    def get_watcher(self) -> "JobWatcher":
        pass
