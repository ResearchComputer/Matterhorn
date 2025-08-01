from typing import TYPE_CHECKING, Callable, Optional

from rcc.core.utils import get_or_raise, NotWatchingError
from .watcher_thread import WatcherThread, WatcherThreadImpl

try:
    from typing import Protocol
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol  # type: ignore


if TYPE_CHECKING:
    from .job_status import BaseJobStatus
    from .batch_job import BaseBatchJob


JobStatusCallback = Callable[["BaseJobStatus"], None]
WatcherThreadFactory = Callable[["BaseBatchJob", JobStatusCallback, int], WatcherThread]


class JobWatcher(Protocol):
    def watch(self, callback: JobStatusCallback, poll_interval: int) -> None:
        """
        Starts watching the job in the background.

        Args:
            callback (JobStatusCallback): A callback that accepts a status update.
            poll_interval (int): The time between poll calls.
        """

    def wait_until_done(self) -> None:
        """
        Blocks until the job has been completed.
        """

    def stop(self) -> None:
        """
        Stops watching the job.
        """


JobWatcherFactory = Callable[["BaseBatchJob"], JobWatcher]


class JobWatcherImpl:
    def __init__(
        self,
        runner: "BaseBatchJob",
        thread_factory: WatcherThreadFactory = WatcherThreadImpl,
    ) -> None:
        self.runner = runner
        self.factory = thread_factory
        self.watching_thread: Optional[WatcherThread] = None

    def watch(self, callback: JobStatusCallback, poll_interval: int) -> None:
        self.watching_thread = self.factory(self.runner, callback, poll_interval)
        self.watching_thread.start()

    def is_done(self) -> bool:
        watching_thread = get_or_raise(self.watching_thread, NotWatchingError)
        return watching_thread.is_done()

    def wait_until_done(self) -> None:
        watching_thread = get_or_raise(self.watching_thread, NotWatchingError)
        self._try_join(watching_thread)

    def stop(self) -> None:
        watching_thread = get_or_raise(self.watching_thread, NotWatchingError)
        watching_thread.stop()
        self._try_join(watching_thread)

    def _try_join(self, watching_thread: WatcherThread) -> None:
        try:
            watching_thread.join()
        except RuntimeError as err:
            print(err)
