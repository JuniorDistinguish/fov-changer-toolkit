"""Overlay driver — draws FOV readout via a transparent DXGI overlay."""
from __future__ import annotations

import logging

from fov_changer_toolkit.models.frame import FovFrame

log = logging.getLogger(__name__)


class OverlayDriver:
    mode = "overlay"

    def __init__(self) -> None:
        self._visible = False

    def attach(self, process_name: str) -> None:
        self._visible = True
        log.info("overlay attached to %s", process_name)

    def write(self, frame: FovFrame) -> None:
        if not self._visible:
            return
        # Rendering hooks live in drivers/cpp/overlay_dxgi.cpp — this is the
        # Python-side state bridge.
        log.debug("overlay fov=%.2f engine=%s", frame.current_fov, frame.engine)

    def detach(self) -> None:
        self._visible = False