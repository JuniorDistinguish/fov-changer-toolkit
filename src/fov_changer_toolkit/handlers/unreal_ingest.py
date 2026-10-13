"""Unreal Engine ingest — reads camera FOV from PlayerCameraManager."""
from __future__ import annotations

import logging
import time
from typing import Iterable

from fov_changer_toolkit.handlers.base_ingest import BaseIngestHandler
from fov_changer_toolkit.models.frame import FovFrame
from fov_changer_toolkit.services.memory_reader import MemoryReader
from fov_changer_toolkit.config.offsets import load_offsets

log = logging.getLogger(__name__)


class UnrealIngestHandler(BaseIngestHandler):
    engine = "unreal"
    known_processes = (
        "shootergame", "tarkov", "fortniteclient-win64-shipping",
        "valore", "gameclient", "helldivers2",
    )

    def stream(self, process_name: str) -> Iterable[FovFrame]:
        offsets = load_offsets(self.engine)
        reader = MemoryReader(process_name)
        reader.open()
        try:
            while True:
                addr = reader.resolve_pointer_chain(offsets["camera_manager"], offsets["fov_chain"])
                raw = reader.read_float(addr)
                if raw is None:
                    yield FovFrame(engine=self.engine, current_fov=0.0, valid=False)
                else:
                    yield FovFrame(engine=self.engine, current_fov=raw, valid=True)
                time.sleep(0.016)
        finally:
            reader.close()