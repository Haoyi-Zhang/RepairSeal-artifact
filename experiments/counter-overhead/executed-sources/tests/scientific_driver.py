"""Entry contracts shared by local scientific drivers.

The retained campaigns use assertions to enforce independent oracle agreement.
They therefore refuse optimized Python before starting work.  Receiver APIs do
not depend on this module and remain usable with optimized Python.
"""
from pathlib import Path


def require_assertions() -> None:
    if not __debug__:
        raise SystemExit(
            "scientific reproduction requires enabled assertions; run without -O or -OO"
        )


def new_output_directory(path: Path) -> Path:
    """Create a new or empty directory without replacing an existing payload."""
    if path.is_symlink():
        raise SystemExit("output must be new or empty; existing evidence is preserved")
    path = path.resolve()
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise SystemExit("output must be new or empty; existing evidence is preserved")
    path.mkdir(parents=True, exist_ok=True)
    return path


def new_output_file(path: Path) -> Path:
    """Reserve a fresh file destination before a potentially expensive run."""
    # A dangling symlink is also an existing destination, even though exists()
    # is false.  Do not follow it and create the target as a side effect.
    if path.exists() or path.is_symlink():
        raise SystemExit("output must be a new file; existing evidence is preserved")
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
