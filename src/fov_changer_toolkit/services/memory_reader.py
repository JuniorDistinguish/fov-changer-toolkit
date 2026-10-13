"""Cross-process memory read/write for FOV patching."""
from __future__ import annotations

import ctypes
import logging
import struct
from ctypes import wintypes

from fov_changer_toolkit.services.process_attach import ProcessAttach

log = logging.getLogger(__name__)


class MemoryReader:
    def __init__(self, process_name: str) -> None:
        self.process_name = process_name
        self._attach = ProcessAttach()
        self._k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._handle: int | None = None
        self._pid: int | None = None

    def open(self) -> None:
        for pid, name in self._attach.enumerate_processes():
            if name.lower() == self.process_name.lower():
                self._pid = pid
                self._handle = self._attach.open_rw(pid)
                log.info("attached %s pid=%d", self.process_name, pid)
                return
        raise RuntimeError(f"process not found: {self.process_name}")

    def close(self) -> None:
        if self._handle:
            self._k32.CloseHandle(self._handle)
            self._handle = None

    def read_bytes(self, addr: int, size: int) -> bytes | None:
        buf = (ctypes.c_char * size)()
        read = ctypes.c_size_t(0)
        ok = self._k32.ReadProcessMemory(self._handle, ctypes.c_void_p(addr), buf, size, ctypes.byref(read))
        if not ok:
            return None
        return buf.raw[: read.value]

    def read_float(self, addr: int) -> float | None:
        raw = self.read_bytes(addr, 4)
        return struct.unpack("<f", raw)[0] if raw else None

    def write_float(self, addr: int, value: float) -> bool:
        data = struct.pack("<f", float(value))
        written = ctypes.c_size_t(0)
        ok = self._k32.WriteProcessMemory(
            self._handle, ctypes.c_void_p(addr), data, len(data), ctypes.byref(written)
        )
        return bool(ok) and written.value == len(data)

    def resolve_pointer_chain(self, base: int, chain: list[int]) -> int:
        """Walk [offsets...] from base. Final element is the field offset."""
        addr = base
        for off in chain[:-1]:
            raw = self.read_bytes(addr + off, 8)
            if not raw:
                raise RuntimeError(f"chain broken at {addr:#x}+{off:#x}")
            addr = struct.unpack("<Q", raw)[0]
        return addr + chain[-1]

    def find_class_instance(self, class_ptr: int) -> int | None:
        """Placeholder for il2cpp/mono class instance lookup — see drivers/cpp."""
        return None