"""Memory driver — writes FOV directly into the target camera struct."""
from __future__ import annotations

import logging

from fov_changer_toolkit.models.frame import FovFrame
from fov_changer_toolkit.services.memory_reader import MemoryReader

log = logging.getLogger(__name__)


class MemoryDriver:
    mode = "memory"

    def __init__(self) -> None:
        self._reader: MemoryReader | None = None
        self._last_addr: int = 0

    def attach(self, process_name: str) -> None:
        self._reader = MemoryReader(process_name)
        self._reader.open()

    def write(self, frame: FovFrame) -> None:
        if self._reader is None or frame.source_addr == 0:
            return
        if self._reader.write_float(frame.source_addr, frame.current_fov):
            self._last_addr = frame.source_addr
        else:
            log.warning("write failed addr=%#x", frame.source_addr)

    def detach(self) -> None:
        if self._reader:
            self._reader.close()
            self._reader = None