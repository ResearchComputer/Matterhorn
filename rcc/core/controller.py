from abc import ABC, abstractmethod
from typing import Optional
from .executor import CommandExecutor, RunningCommand
from rcc.core.utils import ClusterError
from .job import JobWatcherFactory, JobWatcherImpl, BaseBatchJob, BaseJobStatus


class BaseController(ABC):
    def __init__(
        self,
        executor: CommandExecutor,
        watcher_factory: Optional[JobWatcherFactory] = None,
    ) -> None:
        self._executor = executor
        self._watcher_factory = watcher_factory or JobWatcherImpl

    @abstractmethod
    def submit(self, jobfile: str) -> BaseBatchJob: ...

    @abstractmethod
    def poll_status(self, jobid: str) -> BaseJobStatus: ...

    @abstractmethod
    def cancel(self, jobid: str) -> None: ...

    def _execute_and_wait_or_raise_on_error(self, command: str) -> RunningCommand:
        cmd = self._executor.exec_command(command)
        exit_code = cmd.wait_until_exit()
        if exit_code != 0:
            raise ClusterError(command)

        return cmd
