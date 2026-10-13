# Contributing to fov-changer-toolkit

Thanks for wanting to push a PR. This repo is a Windows desktop FOV changer toolkit — pipeline architecture: ingest handlers feed processors, processors feed output drivers. Keep that shape.

## Ground rules

- Python 3.11+ is the reference runtime. C++ (MSVC 19.38+), C# (.NET 8), and Java (17+) drivers live under `drivers/` and are optional accelerators.
- Every PR that touches `core/` must keep the pipeline contract intact: ingest → process → drive. No shortcuts that skip a stage.
- No hardcoded game offsets. Offsets go in `config/offsets.toml` and get versioned per game build.
- Type hints required on all public functions. `mypy --strict` must pass on `core/`, `handlers/`, `services/`.

## Local dev

    python -m venv .venv
    .venv\Scripts\activate
    pip install -e ".[dev]"
    pytest -q

## Commit style

Conventional commits. `feat(handlers): add dxgi overlay ingest`. `fix(processors): clamp fov above 179`.

## PR checklist

- [ ] Tests added or updated under `tests/`
- [ ] `ruff check .` clean
- [ ] `mypy core handlers services` clean
- [ ] Offsets table updated if a game patch landed
- [ ] No binary blobs committed — drivers build from source

## Code of conduct

Don't be a dick. Technical disagreement is fine. Personal attacks get you bounced.