"""FOV pipeline orchestrator.

Contract: every run is discover -> ingest -> process -> drive.
Handlers produce FovFrame objects; processors transform them; drivers
write the result into the target. No stage is skippable.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Iterable

from fov_changer_toolkit.core.registry import DriverRegistry, HandlerRegistry
from fov_changer_toolkit.models.frame import FovFrame
from fov_changer_toolkit.models.profile import FovProfile
from fov_changer_toolkit.models.target import GameTarget

log = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineStats:
    frames: int = 0
    writes: int = 0
    dropped: int = 0
    elapsed_ms: float = 0.0


class FovPipeline:
    """Wires handlers -> processors -> drivers for a single profile run."""

    def __init__(self, handlers: HandlerRegistry, drivers: DriverRegistry) -> None:
        self._handlers = handlers
        self._drivers = drivers

    def discover(self) -> Iterable[GameTarget]:
        for handler in self._handlers.all():
            yield from handler.discover()

    def run(self, profile: FovProfile, target_fov: float, *, duration_s: float | None = None) -> PipelineStats:
        stats = PipelineStats()
        start = time.perf_counter()
        handler = self._handlers.pick(profile.engine)
        driver = self._drivers.pick(profile.mode)

        if handler is None or driver is None:
            raise RuntimeError(f"no handler/driver for engine={profile.engine} mode={profile.mode}")

        driver.attach(profile.process_name)

        try:
            for frame in handler.stream(profile.process_name):
                if not isinstance(frame, FovFrame):
                    stats.dropped += 1
                    continue
                adjusted = frame.with_target(target_fov, profile.clamp)
                if adjusted is None:
                    stats.dropped += 1
                    continue
                driver.write(adjusted)
                stats.frames += 1
                stats.writes += 1
                if duration_s is not None and (time.perf_counter() - start) > duration_s:
                    break
        finally:
            driver.detach()

        stats.elapsed_ms = (time.perf_counter() - start) * 1000.0
        log.info("pipeline done frames=%d writes=%d dropped=%d", stats.frames, stats.writes, stats.dropped)
        return stats