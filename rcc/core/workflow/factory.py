from typing import Any, Callable, Dict, Type

from . import workflow
from rcc.core.filesystem import FilesystemFactory
from rcc.core.utils import (
    FinalizeOptions,
    JobBasedOptions,
    LaunchOptions,
    Options,
    ImmediateCommandOptions,
    WatchOptions,
)
from rcc.cluster._base import Controller
from .workflow import Workflow


def _immediate_cmd_workflow(
    controller: Controller,
    immediate_cmd_options: ImmediateCommandOptions,
) -> Workflow:
    immediate_workflows = {
        ImmediateCommandOptions.Action.status: workflow.statusworkflow,
        ImmediateCommandOptions.Action.cancel: workflow.cancelworkflow,
    }

    workflow = immediate_workflows[immediate_cmd_options.action]
    return workflow(controller, immediate_cmd_options)


_SimpleWorkflowBuilder = Callable[[Controller, Any], Workflow]
_SimpleWorkFlowRegistry = Dict[Type[JobBasedOptions], _SimpleWorkflowBuilder]

_SimpleWorkflows: _SimpleWorkFlowRegistry = {
    ImmediateCommandOptions: _immediate_cmd_workflow,
    WatchOptions: workflow.watchworkflow,
}


def make_workflow(
    filesystem_factory: FilesystemFactory,
    controller: Controller,
    options: Options,
) -> Workflow:
    if isinstance(options, LaunchOptions):
        return workflow.launchworkflow(filesystem_factory, controller, options)
    elif isinstance(options, FinalizeOptions):
        return workflow.finalizeworkflow(filesystem_factory, options)

    option_type = type(options)
    monitoring_workflow_builder = _SimpleWorkflows[option_type]
    return monitoring_workflow_builder(controller, options)
