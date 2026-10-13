"""Entry bootstrap — CLI surface for the FOV changer pipeline."""
from __future__ import annotations

import typer
from rich.console import Console

from fov_changer_toolkit.core.pipeline import FovPipeline
from fov_changer_toolkit.core.registry import HandlerRegistry, DriverRegistry
from fov_changer_toolkit.services.profile_store import ProfileStore
from fov_changer_toolkit.utils.logging_setup import init_logging

app = typer.Typer(add_completion=False, help="FOV changer toolkit — pipeline CLI")
console = Console()


@app.command()
def scan() -> None:
    """Enumerate attachable game processes with known FOV signatures."""
    init_logging()
    pipeline = FovPipeline(HandlerRegistry.default(), DriverRegistry.default())
    for target in pipeline.discover():
        console.print(f"[green]{target.pid:>6}[/]  {target.name:<32} {target.engine}")


@app.command()
def apply(profile: str, value: float) -> None:
    """Apply a FOV value using a named profile."""
    init_logging()
    store = ProfileStore()
    prof = store.load(profile)
    pipeline = FovPipeline(HandlerRegistry.default(), DriverRegistry.default())
    pipeline.run(prof, target_fov=value)
    console.print(f"[bold green]fov set[/] {prof.name} -> {value}")


@app.command()
def profiles() -> None:
    """List saved FOV profiles."""
    for p in ProfileStore().list():
        console.print(f"{p.name:<24} fov={p.target_fov:<6} mode={p.mode}")


if __name__ == "__main__":
    app()