"""Unity ingest — Camera.fieldOfView via mono/il2cpp runtime scan."""
from __future__ import annotations

import logging
import time
from typing import Iterable

from fov_changer_toolkit.handlers.base_ingest import BaseIngestHandler
from fov_changer_toolkit.models.frame import FovFrame
from fov_changer_toolkit.services.memory_reader import MemoryReader
from fov_changer_toolkit.config.offsets import load_offsets

log = logging.getLogger(__name__)


class UnityIngestHandler(BaseIngestHandler):
    engine = "unity"
    known_processes = (
        "rustclient", "escapefromtarkov", "valheim", "genshinimpact",
        "phasmophobia", "lethalcompany",
    )

    def stream(self, process_name: str) -> Iterable[FovFrame]:
        offsets = load_offsets(self.engine)
        reader = MemoryReader(process_name)
        reader.open()
        try:
            while True:
                camera = reader.find_class_instance(offsets["camera_class"])
                if camera is None:
                    yield FovFrame(engine=self.engine, current_fov=0.0, valid=False)
                else:
                    raw = reader.read_float(camera + offsets["fov_field"])
                    yield FovFrame(engine=self.engine, current_fov=raw or 0.0, valid=raw is not None)
                time.sleep(0.016)
        finally:
            reader.close()