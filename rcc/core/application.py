from rcc.core.utils import get_error_message
from rcc.core.executor import CommandExecutor
from rcc.core.filesystem import FilesystemFactory
from rcc.core.utils import Options
from rcc.cluster.slurm.controller import SlurmController

from rcc.core.workflow import Workflow
from rcc.core.workflow import make_workflow
from rcc.core.ui import UI


class Application:
    def __init__(
        self, executor: CommandExecutor, filesystem_factory: FilesystemFactory, ui: UI
    ) -> None:
        self._executor = executor
        self.fs_factory = filesystem_factory
        self._ui = ui
        self._workflow = Workflow([])

    def run(self, options: Options) -> int:
        try:
            return self._run_workflow(options)
        except Exception as err:
            self._ui.error(get_error_message(err))
            return 1

    def _run_workflow(self, options: Options) -> int:
        with self._executor as executor:
            self._workflow = self._get_workflow(executor, options)
            success = self._workflow.run(self._ui)
            return 0 if success else 1

    def _get_workflow(self, executor: CommandExecutor, options: Options) -> Workflow:
        controller = SlurmController(executor)
        return make_workflow(self.fs_factory, controller, options)

    def cancel(self) -> int:
        self._workflow.cancel(self._ui)
        return 130
