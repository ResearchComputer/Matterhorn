from typing import List, Optional

from matterhorn.core.utils import get_or_raise
from matterhorn.core.ui import UI
from matterhorn.core.filesystem import FilesystemFactory
from matterhorn.core.ui import UI
from matterhorn.core.utils import (
    LaunchOptions,
    ImmediateCommandOptions,
    WatchOptions,
    FinalizeOptions,
)
from matterhorn.core.job import BaseBatchJob
from matterhorn.cluster._base import Controller
from .stages import (
    LaunchStage,
    PrepareStage,
    JobLoggingStage,
    WatchStage,
    FinalizeStage,
    CancelStage,
    StatusStage,
)
from typing import List
from pathlib import Path

try:
    from typing import Protocol
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol  # type: ignore


class Stage(Protocol):
    """
    An isolated step that is part of a larger Workflow
    """

    def allowed_to_fail(self) -> bool:
        """
        Returns whether this stage is allowed to fail
        """
        ...

    def __call__(self, ui: UI) -> bool:
        """
        Starts running the stage. Returns true if the stage completed successfully.

        Args:
            ui (UI): The ui to send output to.

        Returns:
            bool
        """
        ...

    def cancel(self, ui: UI) -> None:
        """
        Cancels the stage.

        Args:
            ui (UI): The ui to send output to.
        """
        ...


class Workflow:
    """
    Represents a series of isolated steps that are executed in order
    """

    def __init__(self, stages: List[Stage]) -> None:
        self._stages = stages
        self._active_stage: Optional[Stage] = None
        self._canceled = False

    def run(self, ui: UI) -> bool:
        """
        Runs the workflow. Returns true if all stages completed successfully.

        Args:
            ui (UI): The ui to send output to.

        Returns:
            bool
        """
        results: List[bool] = []
        for stage in self._stages:
            self._active_stage = stage

            if self._canceled:
                break

            result = stage(ui)
            results.append(result)
            if self._workflow_failed(stage, result):
                return False

        return all(results)

    def _workflow_failed(self, stage: Stage, result: bool) -> bool:
        return not (result or stage.allowed_to_fail())

    def cancel(self, ui: UI) -> None:
        """
        Cancels the workflow.

        Args:
            ui (UI): The ui to send output to.

        Raises:
            WorkflowNotStartedError: If the workflow is canceled before it was started.
        """
        active_stage = get_or_raise(self._active_stage, WorkflowNotStartedError)
        active_stage.cancel(ui)
        self._canceled = True


class WorkflowNotStartedError(Exception):
    pass


def launchworkflow(
    filesystem_factory: FilesystemFactory,
    controller: Controller,
    options: LaunchOptions,
) -> Workflow:
    launch_stage = LaunchStage(controller, options.sbatch)
    stages: List[Stage] = [
        PrepareStage(filesystem_factory, options.copy_files),
        launch_stage,
    ]

    if options.job_id_file:
        stages.append(JobLoggingStage(launch_stage, Path(options.job_id_file)))

    if options.watch:
        stages.append(
            WatchStage(
                launch_stage, options.poll_interval, options.continue_if_job_fails
            )
        )
        stages.append(
            FinalizeStage(
                filesystem_factory, options.collect_files, options.clean_files
            )
        )

    return Workflow(stages)


def statusworkflow(
    controller: Controller, options: ImmediateCommandOptions
) -> Workflow:
    return Workflow([StatusStage(controller, options.jobid)])


def cancelworkflow(
    controller: Controller, options: ImmediateCommandOptions
) -> Workflow:
    return Workflow([CancelStage(controller, options.jobid)])


def watchworkflow(controller: Controller, options: WatchOptions) -> Workflow:
    class SimpleBatchJobProvider:
        def get_batch_job(self) -> BaseBatchJob:
            return BaseBatchJob(controller, options.jobid)

        def cancel(self, ui: UI) -> None:
            pass

    return Workflow([WatchStage(SimpleBatchJobProvider(), options.poll_interval)])


def finalizeworkflow(
    filesystem_factory: FilesystemFactory,
    options: FinalizeOptions,
) -> Workflow:
    return Workflow(
        [FinalizeStage(filesystem_factory, options.collect_files, options.clean_files)]
    )
