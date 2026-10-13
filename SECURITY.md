# Security Policy

## Scope

fov-changer-toolkit runs with elevated privileges on Windows to attach to game processes and patch camera FOV. That's the whole point. It also means every module in `services/` is a potential privilege boundary.

## Reporting a vulnerability

Open a private security advisory on GitHub. Do not file a public issue for anything that lets a non-elevated process hijack our handle table, inject through our driver channel, or persist arbitrary code via the config loader. We'll respond within 72 hours.

## What we consider in-scope

- Handle escalation via `services/process_attach.py`
- Signature bypass in `drivers/cpp/attach_win32.cpp` that affects other processes
- Config injection through `config/loader.py` (TOML parse → arbitrary path write)
- Unsigned payload acceptance in `services/driver_channel.py`

## What we do not consider in-scope

- Anti-cheat detection of the tool itself. That is a game-policy matter, not a toolkit vulnerability.
- Game bans resulting from use. Read the disclaimer in `docs/`.
- Third-party forks that strip the signature check.

## Disclosure

90-day coordinated disclosure. After that we publish the advisory and a patched release.