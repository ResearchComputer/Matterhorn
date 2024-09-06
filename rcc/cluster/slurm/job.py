from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING
from rcc.core.job import (
    BaseJobStatus,
    TaskStatus,
    JobWatcherFactory,
    JobWatcherImpl,
    JobWatcher,
    BaseBatchJob,
)

if TYPE_CHECKING:
    from .controller import SlurmController


@dataclass
class SlurmJobStatus(BaseJobStatus):
    @classmethod
    def empty(cls) -> "SlurmJobStatus":
        return SlurmJobStatus("", "", "", [])

    @classmethod
    def from_output(cls, output: List[str]) -> "SlurmJobStatus":
        tasks = [TaskStatus(*line.split()[:3]) for line in output if line]

        main_task = tasks[0] if tasks else TaskStatus("", "", "")

        return SlurmJobStatus(
            id=main_task.id, name=main_task.name, state=main_task.state, tasks=tasks
        )

    id: str
    name: str
    state: str
    tasks: List[TaskStatus]

    @property
    def is_pending(self) -> bool:
        return self.state == "PENDING"

    @property
    def is_running(self) -> bool:
        return self.state == "RUNNING"

    @property
    def is_completed(self) -> bool:
        return self.state == "COMPLETED"

    @property
    def success(self) -> bool:
        return self.state == "COMPLETED" and all(
            task.state == "COMPLETED" for task in self.tasks
        )


class SlurmBatchJob(BaseBatchJob):
    def __init__(
        self,
        controller: "SlurmController",
        jobid: str = "",
        watcher_factory: Optional[JobWatcherFactory] = None,
    ):
        self._controller = controller
        self._watcher_factory = watcher_factory or JobWatcherImpl
        self.jobid = jobid

    def cancel(self) -> None:
        self._controller.cancel(self.jobid)

    def poll_status(self) -> SlurmJobStatus:
        return self._controller.poll_status(self.jobid)

    def get_watcher(self) -> JobWatcher:
        return self._watcher_factory(self)
