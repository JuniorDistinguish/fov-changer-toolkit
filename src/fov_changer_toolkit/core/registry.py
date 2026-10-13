"""Handler and driver registries — plugin lookup by engine/mode."""
from __future__ import annotations

from typing import Iterable, Protocol

from fov_changer_toolkit.models.target import GameTarget
from fov_changer_toolkit.models.frame import FovFrame


class IngestHandler(Protocol):
    engine: str

    def discover(self) -> Iterable[GameTarget]: ...
    def stream(self, process_name: str) -> Iterable[FovFrame]: ...


class OutputDriver(Protocol):
    mode: str

    def attach(self, process_name: str) -> None: ...
    def write(self, frame: FovFrame) -> None: ...
    def detach(self) -> None: ...


class HandlerRegistry:
    def __init__(self, handlers: list[IngestHandler] | None = None) -> None:
        self._handlers = handlers or []

    @classmethod
    def default(cls) -> "HandlerRegistry":
        from fov_changer_toolkit.handlers.unreal_ingest import UnrealIngestHandler
        from fov_changer_toolkit.handlers.unity_ingest import UnityIngestHandler
        from fov_changer_toolkit.handlers.source_ingest import SourceIngestHandler
        return cls([UnrealIngestHandler(), UnityIngestHandler(), SourceIngestHandler()])

    def all(self) -> Iterable[IngestHandler]:
        return list(self._handlers)

    def pick(self, engine: str) -> IngestHandler | None:
        for h in self._handlers:
            if h.engine == engine:
                return h
        return None


class DriverRegistry:
    def __init__(self, drivers: list[OutputDriver] | None = None) -> None:
        self._drivers = drivers or []

    @classmethod
    def default(cls) -> "DriverRegistry":
        from fov_changer_toolkit.drivers.memory_driver import MemoryDriver
        from fov_changer_toolkit.drivers.overlay_driver import OverlayDriver
        return cls([MemoryDriver(), OverlayDriver()])

    def all(self) -> Iterable[OutputDriver]:
        return list(self._drivers)

    def pick(self, mode: str) -> OutputDriver | None:
        for d in self._drivers:
            if d.mode == mode:
                return d
        return None