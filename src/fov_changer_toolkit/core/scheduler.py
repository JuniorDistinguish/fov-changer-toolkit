"""Worker scheduler — ticks the pipeline on a fixed cadence."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable

@dataclass(slots=True)
class TickConfig:
    interval_ms: int = 16
    jitter_ms: int = 2
    max_ticks: int | None = None


@dataclass(slots=True)
class SchedulerState:
    ticks: int = 0
    overruns: int = 0
    stop_flag: threading.Event = field(default_factory=threading.Event)


class WorkerScheduler:
    """Runs a callable on a fixed interval in a background thread."""

    def __init__(self, cfg: TickConfig) -> None:
        self.cfg = cfg
        self.state = SchedulerState()
        self._thread: threading.Thread | None = None

    def start(self, fn: Callable[[int], None]) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, args=(fn,), daemon=True, name="fov-scheduler")
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        self.state.stop_flag.set()
        if self._thread:
            self._thread.join(timeout)

    def _loop(self, fn: Callable[[int], None]) -> None:
        interval = self.cfg.interval_ms / 1000.0
        next_tick = time.perf_counter()
        while not self.state.stop_flag.is_set():
            now = time.perf_counter()
            if now < next_tick:
                time.sleep(next_tick - now)
            started = time.perf_counter()
            try:
                fn(self.state.ticks)
            except Exception:
                self.state.overruns += 1
            elapsed = time.perf_counter() - started
            if elapsed > interval:
                self.state.overruns += 1
            self.state.ticks += 1
            if self.cfg.max_ticks is not None and self.state.ticks >= self.cfg.max_ticks:
                break
            next_tick = started + interval