"""GameTarget — a discovered attachable process."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class GameTarget:
    pid: int
    name: str
    engine: str

    def __str__(self) -> str:
        return f"{self.name}({self.pid}) [{self.engine}]"