"""Core settings for INKY.

This module intentionally has no pygame side effects at import time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

WIDTH: Final = 1200
HEIGHT: Final = 800
TITLE: Final = "INKY: Retro Remix"
FPS: Final = 60
FONT_NAME: Final = "freesansbold.ttf"

# Player movement
PLAYER_ACC: Final = 0.9
PLAYER_FRICTION: Final = -0.18
PLAYER_MAX_SPEED: Final = 11

# Gameplay tuning
MAX_INK: Final = 255

# Basic colors
WHITE: Final = (255, 255, 255)
BLACK: Final = (0, 0, 0)
RED: Final = (255, 72, 72)
GREEN: Final = (85, 235, 120)
BLUE: Final = (90, 130, 255)
PURPLE: Final = (170, 95, 240)
YELLOW: Final = (250, 220, 95)
TEAL: Final = (70, 220, 220)
GREY: Final = (100, 100, 100)
GOLD: Final = (255, 210, 90)

# UI and background
BG_DARK: Final = (10, 14, 24)
BG_MID: Final = (19, 30, 50)
BG_GRID: Final = (36, 57, 87)
HUD_PANEL: Final = (22, 34, 58)
HUD_BORDER: Final = (77, 117, 181)


@dataclass(frozen=True)
class GamePalette:
    bg_dark: tuple[int, int, int] = BG_DARK
    bg_mid: tuple[int, int, int] = BG_MID
    bg_grid: tuple[int, int, int] = BG_GRID
    hud_panel: tuple[int, int, int] = HUD_PANEL
    hud_border: tuple[int, int, int] = HUD_BORDER
    red: tuple[int, int, int] = RED
    green: tuple[int, int, int] = GREEN
    blue: tuple[int, int, int] = BLUE
    purple: tuple[int, int, int] = PURPLE
    yellow: tuple[int, int, int] = YELLOW
    teal: tuple[int, int, int] = TEAL


PALETTE: Final = GamePalette()



