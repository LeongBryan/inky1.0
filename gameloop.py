"""Compatibility entry point.

This module keeps the old filename while delegating to the modern game loop.
"""

from __future__ import annotations

from main import main


if __name__ == "__main__":
    main()
