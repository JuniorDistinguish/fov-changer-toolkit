"""Process enumeration and handle acquisition (Windows)."""
from __future__ import annotations

import ctypes
import logging
from ctypes import wintypes
from typing import Iterator

log = logging.getLogger(__name__)

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260),
    ]


class ProcessAttach:
    def __init__(self) -> None:
        self._k32 = ctypes.WinDLL("kernel32", use_last_error=True)

    def enumerate_processes(self) -> Iterator[tuple[int, str]]:
        snap = self._k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snap == INVALID_HANDLE_VALUE:
            log.warning("snapshot failed: %d", ctypes.get_last_error())
            return
        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
        try:
            ok = self._k32.Process32First(snap, ctypes.byref(entry))
            while ok:
                yield int(entry.th32ProcessID), entry.szExeFile.decode("ascii", "ignore")
                ok = self._k32.Process32Next(snap, ctypes.byref(entry))
        finally:
            self._k32.CloseHandle(snap)

    def open_rw(self, pid: int) -> int:
        """Open with RW + VM_OPERATION. Caller owns the handle."""
        access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION
        handle = self._k32.OpenProcess(access, False, pid)
        if not handle:
            raise OSError(f"OpenProcess failed pid={pid} err={ctypes.get_last_error()}")
        return handle