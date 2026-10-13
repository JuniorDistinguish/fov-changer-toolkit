"""Profile store — TOML/JSON persistence in %APPDATA%\\fov-changer-toolkit."""
from __future__ import annotations

import json
import os
from pathlib import Path

from fov_changer_toolkit.models.profile import FovProfile


def _root() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    p = Path(base) / "fov-changer-toolkit" / "profiles"
    p.mkdir(parents=True, exist_ok=True)
    return p


class ProfileStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or _root()

    def _path(self, name: str) -> Path:
        safe = "".join(c for c in name if c.isalnum() or c in "-_")
        return self.root / f"{safe}.json"

    def save(self, profile: FovProfile) -> Path:
        p = self._path(profile.name)
        p.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
        return p

    def load(self, name: str) -> FovProfile:
        p = self._path(name)
        if not p.exists():
            raise FileNotFoundError(f"profile not found: {name}")
        return FovProfile.model_validate_json(p.read_text(encoding="utf-8"))

    def list(self) -> list[FovProfile]:
        out: list[FovProfile] = []
        for f in sorted(self.root.glob("*.json")):
            try:
                out.append(FovProfile.model_validate_json(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        return out