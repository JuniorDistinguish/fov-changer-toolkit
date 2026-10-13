"""FovProfile — a saved FOV configuration."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class FovProfile(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    engine: str = Field(pattern=r"^(unreal|unity|source|generic)$")
    process_name: str = Field(min_length=1, max_length=128)
    mode: str = Field(default="memory", pattern=r"^(memory|overlay|dxgi)$")
    target_fov: float = Field(default=110.0, ge=1.0, le=179.0)
    clamp: tuple[float, float] = (60.0, 179.0)
    smoothing: float = Field(default=0.0, ge=0.0, le=1.0)
    hotkey_toggle: str = "f7"

    @field_validator("clamp")
    @classmethod
    def _clamp_ordered(cls, v: tuple[float, float]) -> tuple[float, float]:
        lo, hi = v
        if lo >= hi:
            raise ValueError("clamp lo must be < hi")
        if hi > 179.0:
            raise ValueError("clamp hi must be <= 179.0 (FOV > 179 breaks most engines)")
        return v