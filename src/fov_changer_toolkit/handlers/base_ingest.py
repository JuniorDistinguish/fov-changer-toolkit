"""Base ingest handler — shared discovery and stream scaffolding."""
from __future__ import annotations

import logging
from typing import Iterable

from fov_changer_toolkit.models.frame import FovFrame
from fov_changer_toolkit.models.target import GameTarget
from fov_changer_toolkit.services.process_attach import ProcessAttach

log = logging.getLogger(__name__)


class BaseIngestHandler:
    engine: str = "unknown"
    known_processes: tuple[str, ...] = ()

    def __init__(self) -> None:
        self._attach = ProcessAttach()

    def discover(self) -> Iterable[GameTarget]:
        for pid, name in self._attach.enumerate_processes():
            stem = name.lower().removesuffix(".exe")
            if any(stem == k for k in self.known_processes):
                yield GameTarget(pid=pid, name=name, engine=self.engine)

    def stream(self, process_name: str) -> Iterable[FovFrame]:
        raise NotImplementedError