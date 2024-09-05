from abc import ABC, abstractmethod
from typing import Optional
from matterhorn.core.executor import CommandExecutor
from matterhorn.core.job.job_watcher import JobWatcherFactory, JobWatcherImpl
from matterhorn.core.job.batch_job import BaseBatchJob
from matterhorn.core.job import BaseJobStatus


class Controller(ABC):
    def __init__(
        self,
        executor: CommandExecutor,
        watcher_factory: Optional[JobWatcherFactory] = None,
    ) -> None:
        self._executor = executor
        self._watcher_factory = watcher_factory or JobWatcherImpl

    @abstractmethod
    def submit(self, jobfile: str) -> "BaseBatchJob": ...

    @abstractmethod
    def poll_status(self, jobid: str) -> "BaseJobStatus": ...

    @abstractmethod
    def cancel(self, jobid: str) -> None: ...
