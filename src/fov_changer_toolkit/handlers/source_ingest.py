"""Source engine ingest — reads fov_desired cvar backing store."""
from __future__ import annotations

import time
from typing import Iterable

from fov_changer_toolkit.handlers.base_ingest import BaseIngestHandler
from fov_changer_toolkit.models.frame import FovFrame
from fov_changer_toolkit.services.memory_reader import MemoryReader
from fov_changer_toolkit.config.offsets import load_offsets


class SourceIngestHandler(BaseIngestHandler):
    engine = "source"
    known_processes = ("cs2", "hl2", "gmod", "portal2", "l4d2")

    def stream(self, process_name: str) -> Iterable[FovFrame]:
        offsets = load_offsets(self.engine)
        reader = MemoryReader(process_name)
        reader.open()
        try:
            while True:
                addr = reader.resolve_pointer_chain(offsets["cvar_base"], offsets["fov_desired"])
                raw = reader.read_float(addr)
                yield FovFrame(engine=self.engine, current_fov=raw or 0.0, valid=raw is not None)
                time.sleep(0.016)
        finally:
            reader.close()