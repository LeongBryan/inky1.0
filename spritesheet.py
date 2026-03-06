"""Utility helpers for sprite sheets."""

from __future__ import annotations

from pathlib import Path

import pygame as pg

IMG_DIR = Path(__file__).resolve().parent / "Images"


class Spritesheet:
    def __init__(self, filename: str) -> None:
        sheet_path = IMG_DIR / filename
        self.sheet = pg.image.load(sheet_path).convert()

    def image_at(
        self,
        rectangle: tuple[int, int, int, int],
        colorkey: tuple[int, int, int] | None = None,
    ) -> pg.Surface:
        """Return a single sprite clipped from the sheet."""
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            image.set_colorkey(colorkey)
        return image

    def images_at(
        self,
        rects: list[tuple[int, int, int, int]],
        colorkey: tuple[int, int, int] | None = None,
    ) -> list[pg.Surface]:
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(
        self,
        rect: tuple[int, int, int, int],
        image_count: int,
        colorkey: tuple[int, int, int] | None = None,
    ) -> list[pg.Surface]:
        clips = [(rect[0] + rect[2] * index, rect[1], rect[2], rect[3]) for index in range(image_count)]
        return self.images_at(clips, colorkey)
