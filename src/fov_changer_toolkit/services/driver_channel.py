"""Driver channel — talks to the C++ helper via named pipe."""
from __future__ import annotations

import json
import logging
import struct
import win32file
import win32pipe

log = logging.getLogger(__name__)

PIPE_NAME = r"\\.\pipe\fov_changer_toolkit"
MAGIC = 0xF0C0


class DriverChannel:
    def __init__(self, timeout_ms: int = 500) -> None:
        self.timeout_ms = timeout_ms
        self._handle = None

    def connect(self, retries: int = 3) -> None:
        for attempt in range(retries):
            try:
                self._handle = win32file.CreateFile(
                    PIPE_NAME,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0, None, win32file.OPEN_EXISTING, 0, None,
                )
                return
            except Exception as e:
                log.debug("pipe connect attempt %d failed: %s", attempt, e)
        raise RuntimeError("driver channel unavailable")

    def send(self, opcode: int, payload: dict) -> dict:
        body = json.dumps(payload).encode()
        packet = struct.pack("<HHI", MAGIC, opcode, len(body)) + body
        win32file.WriteFile(self._handle, packet)
        _, resp = win32file.ReadFile(self._handle, 4096)
        return json.loads(resp.decode())

    def close(self) -> None:
        if self._handle:
            self._handle.Close()
            self._handle = None