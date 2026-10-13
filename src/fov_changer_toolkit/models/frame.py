"""FovFrame — one sampled camera FOV reading."""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(slots=True, frozen=True)
class FovFrame:
    engine: str
    current_fov: float
    valid: bool
    timestamp_ms: int = 0
    source_addr: int = 0

    def with_target(self, target: float, clamp: tuple[float, float]) -> "FovFrame | None":
        if not self.valid:
            return None
        lo, hi = clamp
        value = max(lo, min(hi, target))
        if abs(value - self.current_fov) < 0.01:
            return None
        return replace(self, current_fov=value)