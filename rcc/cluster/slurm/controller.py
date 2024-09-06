from typing import Optional
from rcc.core.executor import CommandExecutor, RunningCommand
from rcc.core.job import JobWatcherFactory, JobWatcherImpl
from rcc.core.utils import ClusterError
from rcc.cluster._base import Controller

from .job import SlurmJobStatus, SlurmBatchJob


class SlurmController(Controller):
    def __init__(
        self,
        executor: CommandExecutor,
        watcher_factory: Optional[JobWatcherFactory] = None,
    ) -> None:
        self._executor = executor
        self._watcher_factory = watcher_factory or JobWatcherImpl

    def submit(self, jobfile: str) -> SlurmBatchJob:
        cmd = self._execute_and_wait_or_raise_on_error(f"sbatch {jobfile}")
        jobid = _parse_jobid(cmd)

        return SlurmBatchJob(self, jobid, self._watcher_factory)

    def poll_status(self, jobid: str) -> SlurmJobStatus:
        cmd = self._execute_and_wait_or_raise_on_error(
            f"sacct -j {jobid} -o jobid,jobname%30,state --noheader"
        )
        return SlurmJobStatus.from_output(cmd.stdout())

    def cancel(self, jobid: str) -> None:
        self._execute_and_wait_or_raise_on_error(f"scancel {jobid}")

    def _execute_and_wait_or_raise_on_error(self, command: str) -> RunningCommand:
        cmd = self._executor.exec_command(command)
        exit_code = cmd.wait_until_exit()
        if exit_code != 0:
            raise ClusterError(command)

        return cmd


def _parse_jobid(cmd: RunningCommand) -> str:
    first_line = cmd.stdout()[0]
    split_line = first_line.split()
    jobid = split_line[-1]

    return jobid
