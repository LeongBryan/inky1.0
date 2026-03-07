from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from pathlib import Path

import pygame as pg

from settings import (
    BG_DARK,
    BG_GRID,
    BG_MID,
    BLACK,
    BLUE,
    FONT_NAME,
    FPS,
    GOLD,
    GREEN,
    HEIGHT,
    HUD_BORDER,
    HUD_PANEL,
    MAX_INK,
    PLAYER_ACC,
    PLAYER_FRICTION,
    PLAYER_MAX_SPEED,
    PURPLE,
    RED,
    TEAL,
    TITLE,
    WHITE,
    WIDTH,
    YELLOW,
)

vec = pg.math.Vector2

ROOT = Path(__file__).resolve().parent
IMG_DIR = ROOT / "Images"
LEADERBOARD_PATH = ROOT / "leaderboard.txt"

CHANNELS = ("red", "green", "blue")


@dataclass(frozen=True)
class EnemyProfile:
    key: str
    target_rgb: tuple[int, int, int]
    tint: tuple[int, int, int]
    points: int


ENEMY_PROFILES: dict[str, EnemyProfile] = {
    "red": EnemyProfile("red", (1, 0, 0), RED, 110),
    "green": EnemyProfile("green", (0, 1, 0), GREEN, 110),
    "blue": EnemyProfile("blue", (0, 0, 1), BLUE, 110),
    "purple": EnemyProfile("purple", (1, 0, 1), PURPLE, 180),
    "teal": EnemyProfile("teal", (0, 1, 1), TEAL, 180),
    "yellow": EnemyProfile("yellow", (1, 1, 0), YELLOW, 180),
}

WAVE_RECIPES: list[list[str]] = [
    ["red", "red"],
    ["green", "green"],
    ["blue", "blue", "blue"],
    ["red", "red", "red", "green"],
    ["green", "green", "blue", "blue"],
    ["red", "red", "green", "green", "blue"],
    ["purple", "red", "blue", "red"],
    ["teal", "green", "blue", "green"],
    ["yellow", "red", "green", "red"],
    ["purple", "teal", "yellow", "red", "green", "blue"],
]


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def parse_leaderboard(path: Path) -> list[tuple[str, int]]:
    if not path.exists():
        return []

    entries: list[tuple[str, int]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    for line in lines:
        if "," not in line:
            continue
        raw_name, raw_score = line.split(",", 1)
        name = raw_name.strip() or "YOU"
        try:
            score = int(raw_score.strip())
        except ValueError:
            continue
        entries.append((name, score))

    entries.sort(key=lambda item: item[1], reverse=True)
    return entries[:5]


def write_leaderboard(path: Path, entries: list[tuple[str, int]]) -> None:
    lines = [f"{name}, {score}" for name, score in entries[:5]]
    try:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError:
        # Browser/wasm targets may not have writable local files.
        return


def record_score(entries: list[tuple[str, int]], score: int, name: str = "YOU") -> list[tuple[str, int]]:
    if score <= 0:
        return entries[:5]

    updated = list(entries)
    updated.append((name, score))
    updated.sort(key=lambda item: item[1], reverse=True)
    return updated[:5]


def load_image(
    filename: str,
    *,
    size: tuple[int, int] | None = None,
    colorkey: tuple[int, int, int] | str | None = None,
    fallback_color: tuple[int, int, int] = WHITE,
    alpha: bool = True,
) -> pg.Surface:
    path = IMG_DIR / filename
    try:
        loaded = pg.image.load(path)
        image = loaded.convert_alpha() if alpha else loaded.convert()
    except (FileNotFoundError, pg.error):
        fallback_size = size or (64, 64)
        flags = pg.SRCALPHA if alpha else 0
        image = pg.Surface(fallback_size, flags)
        image.fill(fallback_color)

    if colorkey is not None:
        if image.get_masks()[3] != 0:
            image = image.convert()

        key = image.get_at((0, 0))[:3] if colorkey == "auto" else colorkey
        image.set_colorkey(key)
        image = image.convert_alpha()

    if size is not None and image.get_size() != size:
        image = pg.transform.scale(image, size)

    return image


def load_frames(
    names: list[str],
    *,
    colorkey: tuple[int, int, int] | str | None = None,
    fallback_color: tuple[int, int, int] = WHITE,
) -> list[pg.Surface]:
    return [
        load_image(name, colorkey=colorkey, fallback_color=fallback_color)
        for name in names
    ]


class AssetPack:
    @staticmethod
    def build_blue_shot(size: int = 52) -> pg.Surface:
        # Build a clean circular blue projectile to avoid square silhouettes.
        shot = pg.Surface((size, size), pg.SRCALPHA)
        center = (size // 2, size // 2)
        radius = size // 2 - 2
        pg.draw.circle(shot, (70, 165, 255), center, radius)
        pg.draw.circle(shot, (210, 240, 255), center, radius - 5, 3)
        pg.draw.circle(shot, (255, 255, 255, 80), (center[0] - 6, center[1] - 6), max(4, radius // 3))
        return shot

    def __init__(self) -> None:
        self.player = load_image("inkydog.png", size=(82, 82), colorkey="auto")

        self.shots = {
            "red": load_image("shot_red.png", size=(15, 34), colorkey="auto"),
            "green": load_image("shot_green.png", size=(18, 18), colorkey="auto"),
            "blue": self.build_blue_shot(),
        }

        self.potions = {
            "red": load_image("red_potion.png", size=(26, 26), colorkey="auto"),
            "green": load_image("green_potion.png", size=(26, 26), colorkey="auto"),
            "blue": load_image("blue_potion.png", size=(26, 26), colorkey="auto"),
        }

        self.splats = {
            "red": load_frames(
                [f"redsplat{i}.png" for i in range(1, 7)],
                colorkey="auto",
                fallback_color=RED,
            ),
            "green": load_frames(
                [f"greensplat{i}.png" for i in range(1, 7)],
                colorkey="auto",
                fallback_color=GREEN,
            ),
            "blue": load_frames(
                [f"bluesplat{i}.png" for i in range(1, 7)],
                colorkey="auto",
                fallback_color=BLUE,
            ),
        }


class RetroBackdrop:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.grid_spacing = 44
        self.grid_scroll = 0
        self.stars = [
            [
                random.randint(0, self.width),
                random.randint(0, self.height),
                random.uniform(0.4, 1.8),
            ]
            for _ in range(140)
        ]

    def update(self) -> None:
        self.grid_scroll = (self.grid_scroll + 1) % self.grid_spacing
        for star in self.stars:
            star[1] += star[2]
            if star[1] > self.height + 2:
                star[0] = random.randint(0, self.width)
                star[1] = -2
                star[2] = random.uniform(0.4, 1.8)

    def draw(self, surface: pg.Surface) -> None:
        surface.fill(BG_DARK)

        for x in range(0, self.width + 1, self.grid_spacing):
            pg.draw.line(surface, BG_MID, (x, 0), (x, self.height), 1)

        for y in range(-self.grid_spacing, self.height + self.grid_spacing, self.grid_spacing):
            pg.draw.line(
                surface,
                BG_GRID,
                (0, y + self.grid_scroll),
                (self.width, y + self.grid_scroll),
                1,
            )

        for x, y, speed in self.stars:
            brightness = int(120 + speed * 70)
            color = (brightness, brightness, brightness)
            surface.fill(color, (int(x), int(y), 2, 2))


class Projectile(pg.sprite.Sprite):
    def __init__(
        self,
        *,
        channel: str,
        pos: tuple[float, float],
        direction: vec,
        image: pg.Surface,
        speed: float,
        damage: int,
        bounce: bool = False,
        spin: bool = False,
        pierce: int = 0,
    ) -> None:
        super().__init__()
        self.channel = channel

        move = direction if direction.length_squared() > 0 else vec(0, -1)
        self.velocity = move.normalize() * speed

        if spin:
            self.base_image = image.copy()
            self.image = self.base_image.copy()
        else:
            angle = vec(0, -1).angle_to(self.velocity)
            self.base_image = pg.transform.rotate(image, -angle)
            self.image = self.base_image.copy()

        self.rect = self.image.get_rect(center=pos)
        self.pos = vec(self.rect.center)
        self.damage = damage
        self.bounce = bounce
        self.spin = spin
        self.pierce = pierce
        self.bounces_left = 3
        self.spawn_time = pg.time.get_ticks()
        self.last_spin_update = self.spawn_time
        self.rotation = 0

    def update(self) -> None:
        self.pos += self.velocity
        self.rect.center = (self.pos.x, self.pos.y)

        if self.spin:
            now = pg.time.get_ticks()
            if now - self.last_spin_update > 35:
                self.last_spin_update = now
                self.rotation = (self.rotation + 16) % 360
                center = self.rect.center
                self.image = pg.transform.rotate(self.base_image, self.rotation)
                self.rect = self.image.get_rect(center=center)

        if self.bounce:
            bounced = False
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.velocity.x *= -1
                bounced = True
            if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
                self.velocity.y *= -1
                bounced = True
            if bounced:
                self.bounces_left -= 1
                if self.bounces_left < 0:
                    self.kill()
        else:
            if (
                self.rect.right < -80
                or self.rect.left > WIDTH + 80
                or self.rect.bottom < -80
                or self.rect.top > HEIGHT + 80
            ):
                self.kill()

        if pg.time.get_ticks() - self.spawn_time > 2200:
            self.kill()


class Enemy(pg.sprite.Sprite):
    def __init__(self, profile: EnemyProfile, wave: int) -> None:
        super().__init__()
        self.profile = profile
        self.size = random.randint(58, 96) + min(20, wave)
        self.image = pg.Surface((self.size, self.size), pg.SRCALPHA)
        self.rect = self.image.get_rect(
            center=(random.randint(80, WIDTH - 80), random.randint(90, HEIGHT - 90))
        )
        self.pos = vec(self.rect.center)

        speed = random.uniform(1.2, 2.2 + wave * 0.05)
        angle = random.uniform(0, 360)
        self.velocity = vec(speed, 0).rotate(angle)

        self.target = {
            "red": bool(profile.target_rgb[0]),
            "green": bool(profile.target_rgb[1]),
            "blue": bool(profile.target_rgb[2]),
        }
        self.ink = {"red": 0.0, "green": 0.0, "blue": 0.0}
        self.hit_flash = 0
        self.refresh_sprite()

    @property
    def required_channels(self) -> list[str]:
        return [channel for channel in CHANNELS if self.target[channel]]

    def is_completed(self) -> bool:
        return all(self.ink[channel] >= MAX_INK for channel in self.required_channels)

    def apply_hit(self, channel: str, amount: int) -> tuple[bool, bool]:
        matched = self.target[channel]
        applied = amount if matched else max(1, int(amount * 0.12))
        self.ink[channel] = clamp(self.ink[channel] + applied, 0, MAX_INK)

        self.hit_flash = 5 if matched else 2
        if matched:
            self.velocity *= 0.97

        return self.is_completed(), matched

    def refresh_sprite(self) -> None:
        r = int(self.ink["red"]) if self.target["red"] else 18
        g = int(self.ink["green"]) if self.target["green"] else 18
        b = int(self.ink["blue"]) if self.target["blue"] else 18

        self.image.fill((r, g, b))
        outline = WHITE if self.hit_flash > 0 else HUD_BORDER
        pg.draw.rect(self.image, outline, self.image.get_rect(), 3)
        pg.draw.rect(self.image, self.profile.tint, self.image.get_rect().inflate(-14, -14), 2)

    def update(self) -> None:
        self.pos += self.velocity
        self.rect.center = (self.pos.x, self.pos.y)

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.velocity.x *= -1
        if self.rect.top <= 82 or self.rect.bottom >= HEIGHT:
            self.velocity.y *= -1

        if self.hit_flash > 0:
            self.hit_flash -= 1

        self.refresh_sprite()


class Splat(pg.sprite.Sprite):
    def __init__(self, frames: list[pg.Surface], center: tuple[int, int], size: int) -> None:
        super().__init__()
        self.frames = frames
        self.frame_index = 0
        self.size = (size, size)
        self.image = pg.transform.smoothscale(self.frames[0], self.size)
        self.rect = self.image.get_rect(center=center)
        self.frame_rate = 52
        self.last_update = pg.time.get_ticks()

    def update(self) -> None:
        now = pg.time.get_ticks()
        if now - self.last_update < self.frame_rate:
            return

        self.last_update = now
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            self.kill()
            return

        center = self.rect.center
        self.image = pg.transform.smoothscale(self.frames[self.frame_index], self.size)
        self.rect = self.image.get_rect(center=center)


class Potion(pg.sprite.Sprite):
    def __init__(self, channel: str, image: pg.Surface, center: tuple[int, int]) -> None:
        super().__init__()
        self.channel = channel
        self.image = image
        self.rect = self.image.get_rect(center=center)
        self.pos = vec(self.rect.center)
        self.velocity = vec(
            random.choice((-1, 1)) * random.uniform(0.8, 1.8),
            random.choice((-1, 1)) * random.uniform(0.8, 1.8),
        )

    def update(self) -> None:
        self.pos += self.velocity
        self.rect.center = self.pos

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.velocity.x *= -1
        if self.rect.top <= 82 or self.rect.bottom >= HEIGHT:
            self.velocity.y *= -1


class Player(pg.sprite.Sprite):
    def __init__(self, image: pg.Surface) -> None:
        super().__init__()
        self.base_image = image
        self.image = image.copy()
        self.rect = self.image.get_rect(center=(WIDTH * 0.82, HEIGHT * 0.55))
        self.pos = vec(self.rect.center)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.facing = vec(0, -1)

        self.ink = {"red": float(MAX_INK), "green": float(MAX_INK), "blue": float(MAX_INK)}
        self.ink_regen_per_second = {"red": 4.2, "green": 3.4, "blue": 5.1}

        self.last_shot = {"red": 0, "green": 0, "blue": 0}
        self.shot_delay_ms = {"red": 90, "green": 180, "blue": 280}
        self.shot_cost = {"red": 2, "green": 9, "blue": 11}
        self.shot_damage = {"red": 20, "green": 42, "blue": 18}
        self.shot_scatter_deg = {"red": 7.0, "green": 7.0, "blue": 7.0}
        self.shot_fan_step_deg = {"red": 9.0, "green": 15.0, "blue": 12.0}

    def update(self, keys: pg.key.ScancodeWrapper) -> None:
        self.acc = vec(0, 0)

        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.acc.x -= PLAYER_ACC
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.acc.x += PLAYER_ACC
        if keys[pg.K_w] or keys[pg.K_UP]:
            self.acc.y -= PLAYER_ACC
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            self.acc.y += PLAYER_ACC

        if self.acc.length_squared() > 0:
            self.facing = self.acc.normalize()

        self.vel += self.acc
        self.vel += self.vel * PLAYER_FRICTION

        if self.vel.length() > PLAYER_MAX_SPEED:
            self.vel.scale_to_length(PLAYER_MAX_SPEED)

        self.pos += self.vel

        if self.pos.x > WIDTH:
            self.pos.x = 0
        elif self.pos.x < 0:
            self.pos.x = WIDTH

        if self.pos.y > HEIGHT:
            self.pos.y = 84
        elif self.pos.y < 84:
            self.pos.y = HEIGHT

        self.rect.center = self.pos
        self.rotate_toward_facing()

    def rotate_toward_facing(self) -> None:
        if self.facing.length_squared() == 0:
            return

        angle = vec(0, -1).angle_to(self.facing)
        center = self.rect.center
        self.image = pg.transform.rotozoom(self.base_image, -angle, 1.0)
        self.rect = self.image.get_rect(center=center)

    def refill(self, channel: str, amount: float) -> None:
        self.ink[channel] = clamp(self.ink[channel] + amount, 0, MAX_INK)

    def refill_all(self, amount: float) -> None:
        for channel in CHANNELS:
            self.refill(channel, amount)

    def regenerate_ink(self, dt_seconds: float) -> None:
        for channel, regen_rate in self.ink_regen_per_second.items():
            self.refill(channel, regen_rate * dt_seconds)

    def is_ink_empty(self) -> bool:
        return all(self.ink[channel] <= 0 for channel in CHANNELS)

    def can_fire(self, channel: str, now_ms: int) -> bool:
        enough_ink = self.ink[channel] >= self.shot_cost[channel]
        cooled_down = now_ms - self.last_shot[channel] >= self.shot_delay_ms[channel]
        return enough_ink and cooled_down

    def shot_count(self, channel: str, wave_level: int) -> int:
        if channel == "red":
            return 1 + int(wave_level >= 5) + int(wave_level >= 10)
        if channel == "green":
            return 1 + int(wave_level >= 3) + int(wave_level >= 7)
        return 1 + int(wave_level >= 6) + int(wave_level >= 11)

    @staticmethod
    def fan_angles(count: int, step_deg: float) -> list[float]:
        center_index = (count - 1) / 2
        return [(index - center_index) * step_deg for index in range(count)]

    def scaled_damage(self, channel: str, wave_level: int) -> int:
        # Progressive but bounded damage growth to keep later waves fair.
        growth = 1.0 + min(0.8, (wave_level - 1) * 0.05)
        return int(self.shot_damage[channel] * growth)

    def create_shot(
        self,
        channel: str,
        assets: AssetPack,
        now_ms: int,
        wave_level: int,
    ) -> list[Projectile]:
        if not self.can_fire(channel, now_ms):
            return []

        self.last_shot[channel] = now_ms
        self.ink[channel] = clamp(self.ink[channel] - self.shot_cost[channel], 0, MAX_INK)

        base_direction = self.facing if self.facing.length_squared() > 0 else vec(0, -1)
        scatter = self.shot_scatter_deg[channel]
        base_direction = base_direction.rotate(random.uniform(-scatter, scatter))

        shots: list[Projectile] = []
        count = self.shot_count(channel, wave_level)
        angles = self.fan_angles(count, self.shot_fan_step_deg[channel])
        damage = self.scaled_damage(channel, wave_level)

        for angle in angles:
            direction = base_direction.rotate(angle)
            if channel == "red":
                shots.append(
                    Projectile(
                        channel="red",
                        pos=self.rect.center,
                        direction=direction,
                        image=assets.shots["red"],
                        speed=14,
                        damage=damage,
                    )
                )
            elif channel == "green":
                shots.append(
                    Projectile(
                        channel="green",
                        pos=self.rect.center,
                        direction=direction,
                        image=assets.shots["green"],
                        speed=8,
                        damage=damage,
                        bounce=True,
                    )
                )
            else:
                shots.append(
                    Projectile(
                        channel="blue",
                        pos=self.rect.center,
                        direction=direction,
                        image=assets.shots["blue"],
                        speed=7,
                        damage=damage,
                        spin=True,
                        pierce=1,
                    )
                )

        return shots


class Game:
    def __init__(self) -> None:
        pg.mixer.pre_init(44100, -16, 2, 512)
        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()

        self.assets = AssetPack()
        self.backdrop = RetroBackdrop(WIDTH, HEIGHT)
        self.scanlines = self.build_scanline_overlay()

        self.font_cache: dict[int, pg.font.Font] = {}
        self.running = True
        self.state = "title"
        self.pause = False

        self.dt_seconds = 1.0 / FPS
        self.tick = 0
        self.game_over_reason = ""

        self.level = 1
        self.score = 0

        self.leaderboard = parse_leaderboard(LEADERBOARD_PATH)
        self.best_score = self.leaderboard[0][1] if self.leaderboard else 0

        self.player = Player(self.assets.player)
        self.enemies = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.effects = pg.sprite.Group()
        self.pickups = pg.sprite.Group()

    def build_scanline_overlay(self) -> pg.Surface:
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        for y in range(0, HEIGHT, 4):
            pg.draw.line(overlay, (0, 0, 0, 25), (0, y), (WIDTH, y), 1)
        return overlay

    def font(self, size: int) -> pg.font.Font:
        cached = self.font_cache.get(size)
        if cached is not None:
            return cached

        try:
            created = pg.font.Font(FONT_NAME, size)
        except (FileNotFoundError, OSError):
            created = pg.font.Font(None, size)

        self.font_cache[size] = created
        return created

    def draw_text(
        self,
        text: str,
        size: int,
        color: tuple[int, int, int],
        x: float,
        y: float,
        *,
        center: bool = True,
        shadow: bool = True,
        surface: pg.Surface | None = None,
    ) -> None:
        target = surface if surface is not None else self.screen
        font = self.font(size)
        if shadow:
            shadow_surface = font.render(text, True, BLACK)
            shadow_rect = shadow_surface.get_rect()
            if center:
                shadow_rect.center = (x + 2, y + 2)
            else:
                shadow_rect.topleft = (x + 2, y + 2)
            target.blit(shadow_surface, shadow_rect)

        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        target.blit(text_surface, text_rect)

    def start_new_run(self) -> None:
        if self.state in {"playing", "wave_clear", "game_over"} and self.score > 0:
            self.persist_score()

        self.state = "playing"
        self.pause = False
        self.level = 1
        self.score = 0
        self.game_over_reason = ""

        self.player = Player(self.assets.player)
        self.clear_level_objects()
        self.spawn_wave(self.level)

    def persist_score(self) -> None:
        self.best_score = max(self.best_score, self.score)
        self.leaderboard = record_score(self.leaderboard, self.score)
        write_leaderboard(LEADERBOARD_PATH, self.leaderboard)

    def clear_level_objects(self) -> None:
        self.enemies.empty()
        self.projectiles.empty()
        self.effects.empty()
        self.pickups.empty()

    def restart_current_level(self) -> None:
        self.state = "playing"
        self.pause = False
        self.game_over_reason = ""

        self.player = Player(self.assets.player)
        self.clear_level_objects()
        self.spawn_wave(self.level)

    def wave_recipe(self, level: int) -> list[str]:
        def enemy_pool_for_level(num: int) -> list[str]:
            pool = ["red", "green", "blue"]
            if num >= 4:
                pool.append("purple")
            if num >= 6:
                pool.append("teal")
            if num >= 8:
                pool.append("yellow")
            return pool

        if level <= len(WAVE_RECIPES):
            recipe = list(WAVE_RECIPES[level - 1])
            bonus_count = (level - 1) // 2
            pool = enemy_pool_for_level(level)
            for _ in range(bonus_count):
                recipe.append(random.choice(pool))
            return recipe

        recipe: list[str] = []
        count = min(6 + level // 2, 16)
        pool = enemy_pool_for_level(level)

        for _ in range(count):
            recipe.append(random.choice(pool))

        if level % 4 == 0:
            recipe.append(random.choice(["purple", "teal", "yellow"]))

        return recipe

    def spawn_wave(self, level: int) -> None:
        self.enemies.empty()
        self.projectiles.empty()
        self.pickups.empty()
        self.player.refill_all(MAX_INK)
        for key in self.wave_recipe(level):
            profile = ENEMY_PROFILES[key]
            enemy = self.build_safe_enemy(profile, level)
            self.enemies.add(enemy)

    def random_enemy_center(self) -> tuple[int, int]:
        return (random.randint(80, WIDTH - 80), random.randint(140, HEIGHT - 90))

    def build_safe_enemy(self, profile: EnemyProfile, level: int) -> Enemy:
        enemy = Enemy(profile, level)
        for _ in range(50):
            enemy.pos = vec(self.random_enemy_center())
            enemy.rect.center = enemy.pos
            enemy_zone = enemy.rect.inflate(30, 30)
            player_zone = self.player.rect.inflate(220, 220)
            overlap_player = enemy_zone.colliderect(player_zone)
            overlap_enemy = any(enemy_zone.colliderect(other.rect.inflate(24, 24)) for other in self.enemies)
            if not overlap_player and not overlap_enemy:
                break
        return enemy

    def update_projectile_collisions(self) -> None:
        for projectile in tuple(self.projectiles):
            hits = pg.sprite.spritecollide(projectile, self.enemies, False)
            if not hits:
                continue

            enemy = hits[0]
            completed, _matched = enemy.apply_hit(projectile.channel, projectile.damage)

            if completed:
                self.handle_enemy_destroyed(enemy)

            if projectile.pierce > 0:
                projectile.pierce -= 1
            else:
                projectile.kill()

    def handle_enemy_destroyed(self, enemy: Enemy) -> None:
        if not enemy.alive():
            return

        enemy.kill()
        self.score += enemy.profile.points + self.level * 7

        best_channel = enemy.required_channels[0] if enemy.required_channels else "red"
        frames = self.assets.splats.get(best_channel, self.assets.splats["red"])
        effect = Splat(frames, enemy.rect.center, enemy.rect.width + 38)
        self.effects.add(effect)

        drop_pool = enemy.required_channels or list(CHANNELS)
        if random.random() < 0.82:
            potion_channel = random.choice(drop_pool)
            potion = Potion(potion_channel, self.assets.potions[potion_channel], enemy.rect.center)
            self.pickups.add(potion)

            if random.random() < 0.33:
                offset_center = (
                    enemy.rect.centerx + random.randint(-22, 22),
                    enemy.rect.centery + random.randint(-22, 22),
                )
                extra_channel = random.choice(drop_pool)
                extra = Potion(extra_channel, self.assets.potions[extra_channel], offset_center)
                self.pickups.add(extra)

    def finish_run(self, reason: str) -> None:
        self.state = "game_over"
        self.pause = False
        self.game_over_reason = reason
        self.best_score = max(self.best_score, self.score)

    def handle_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                return

            if event.type != pg.KEYDOWN:
                continue

            if event.key == pg.K_ESCAPE:
                if self.score > 0:
                    self.persist_score()
                self.running = False
                return

            if event.key == pg.K_RETURN:
                if self.state == "title":
                    self.start_new_run()
                elif self.state == "wave_clear":
                    self.state = "playing"
                    self.spawn_wave(self.level)
                elif self.state == "game_over":
                    self.restart_current_level()

            if event.key == pg.K_r and self.state in {"playing", "wave_clear", "game_over"}:
                self.start_new_run()

            if event.key == pg.K_p and self.state == "playing":
                self.pause = not self.pause

    def handle_shooting(self, keys: pg.key.ScancodeWrapper) -> None:
        now = pg.time.get_ticks()
        key_map = {
            pg.K_z: "red",
            pg.K_x: "green",
            pg.K_c: "blue",
        }

        for key_code, channel in key_map.items():
            if not keys[key_code]:
                continue

            shots = self.player.create_shot(channel, self.assets, now, self.level)
            for shot in shots:
                self.projectiles.add(shot)

    def update_play_state(self) -> None:
        if self.pause:
            return

        keys = pg.key.get_pressed()
        self.player.update(keys)
        self.handle_shooting(keys)
        self.player.regenerate_ink(self.dt_seconds)

        self.projectiles.update()
        self.enemies.update()
        self.pickups.update()
        self.effects.update()

        self.update_projectile_collisions()

        if pg.sprite.spritecollide(self.player, self.enemies, False, pg.sprite.collide_rect_ratio(0.75)):
            self.finish_run("A chroma block collided with you.")
            return

        pickups = pg.sprite.spritecollide(self.player, self.pickups, dokill=True)
        for pickup in pickups:
            self.player.refill(pickup.channel, 78)

        if self.player.is_ink_empty():
            self.finish_run("All ink channels are empty.")
            return

        if len(self.enemies) == 0:
            self.state = "wave_clear"
            self.level += 1

    def update(self) -> None:
        self.tick += 1
        self.backdrop.update()

        if self.state == "playing":
            self.update_play_state()

    def draw_meter(
        self,
        *,
        label: str,
        value: float,
        max_value: float,
        color: tuple[int, int, int],
        rect: pg.Rect,
        surface: pg.Surface | None = None,
        alpha: int = 220,
    ) -> None:
        target = surface if surface is not None else self.screen

        panel_col = (*HUD_PANEL, max(90, min(255, alpha + 15)))
        border_col = (*HUD_BORDER, max(110, min(255, alpha + 35)))
        pg.draw.rect(target, panel_col, rect, border_radius=6)
        pg.draw.rect(target, border_col, rect, 2, border_radius=6)

        fill_pct = clamp(value / max_value, 0, 1)
        fill_rect = rect.inflate(-6, -10)
        fill_rect.width = int(fill_rect.width * fill_pct)

        if fill_rect.width > 0:
            fill_col = (*color, min(255, alpha + 20))
            pg.draw.rect(target, fill_col, fill_rect, border_radius=4)

        self.draw_text(
            f"{label}: {int(value):03d}",
            20,
            WHITE,
            rect.left + 10,
            rect.centery,
            center=False,
            shadow=False,
            surface=target,
        )

    def draw_hud(self) -> None:
        panel = pg.Rect(12, 10, WIDTH - 24, 120)
        overlap_count = sum(1 for enemy in self.enemies if enemy.rect.colliderect(panel))
        hud_alpha = max(95, 220 - overlap_count * 30)

        hud_surface = pg.Surface(panel.size, pg.SRCALPHA)
        pg.draw.rect(hud_surface, (*HUD_PANEL, hud_alpha), hud_surface.get_rect(), border_radius=8)
        pg.draw.rect(hud_surface, (*HUD_BORDER, min(255, hud_alpha + 25)), hud_surface.get_rect(), 3, border_radius=8)

        self.draw_text(f"WAVE {self.level:02d}", 30, GOLD, 93, 28, surface=hud_surface)
        self.draw_text(f"SCORE {self.score}", 28, WHITE, panel.width // 2, 28, surface=hud_surface)
        self.draw_text(f"BEST {self.best_score}", 24, WHITE, panel.width - 128, 28, surface=hud_surface)

        meter_top = 70
        meter_width = 360
        meter_height = 34
        gap = 20
        x = 13

        self.draw_meter(
            label="RED",
            value=self.player.ink["red"],
            max_value=MAX_INK,
            color=RED,
            rect=pg.Rect(x, meter_top, meter_width, meter_height),
            surface=hud_surface,
            alpha=hud_alpha,
        )
        self.draw_meter(
            label="GREEN",
            value=self.player.ink["green"],
            max_value=MAX_INK,
            color=GREEN,
            rect=pg.Rect(x + meter_width + gap, meter_top, meter_width, meter_height),
            surface=hud_surface,
            alpha=hud_alpha,
        )
        self.draw_meter(
            label="BLUE",
            value=self.player.ink["blue"],
            max_value=MAX_INK,
            color=BLUE,
            rect=pg.Rect(x + (meter_width + gap) * 2, meter_top, meter_width, meter_height),
            surface=hud_surface,
            alpha=hud_alpha,
        )
        self.screen.blit(hud_surface, panel.topleft)

    def draw_title_screen(self) -> None:
        self.draw_text("INKY", 124, GOLD, WIDTH // 2, HEIGHT * 0.22)
        self.draw_text("Retro Remix", 38, WHITE, WIDTH // 2, HEIGHT * 0.31)

        self.draw_text("Move: WASD or Arrow Keys", 28, WHITE, WIDTH // 2, HEIGHT * 0.45)
        self.draw_text("Shoot: Z (Red)  X (Green)  C (Blue)", 28, WHITE, WIDTH // 2, HEIGHT * 0.50)
        self.draw_text("Ink slowly regenerates over time", 26, WHITE, WIDTH // 2, HEIGHT * 0.55)
        self.draw_text("Pause: P   Restart run: R", 24, WHITE, WIDTH // 2, HEIGHT * 0.60)

        blink = (self.tick // 30) % 2 == 0
        if blink:
            self.draw_text("PRESS ENTER TO PLAY", 40, GOLD, WIDTH // 2, HEIGHT * 0.72)

        self.draw_text("TOP PILOTS", 36, WHITE, WIDTH // 2, HEIGHT * 0.80)

        rows = self.leaderboard or [("YOU", 0)]
        for idx, (name, score) in enumerate(rows[:5], start=1):
            y = HEIGHT * 0.84 + idx * 24
            self.draw_text(f"{idx}. {name:<8} {score:>6}", 22, WHITE, WIDTH // 2, y)

    def draw_wave_clear_overlay(self) -> None:
        panel = pg.Surface((700, 250), pg.SRCALPHA)
        panel.fill((15, 22, 42, 220))
        self.screen.blit(panel, (WIDTH // 2 - 350, HEIGHT // 2 - 130))
        pg.draw.rect(self.screen, HUD_BORDER, (WIDTH // 2 - 350, HEIGHT // 2 - 130, 700, 250), 3)

        self.draw_text("WAVE CLEAR", 58, GOLD, WIDTH // 2, HEIGHT // 2 - 45)
        self.draw_text(f"Next: Wave {self.level}", 34, WHITE, WIDTH // 2, HEIGHT // 2 + 12)
        self.draw_text("ENTER to continue", 30, WHITE, WIDTH // 2, HEIGHT // 2 + 68)

    def draw_pause_overlay(self) -> None:
        panel = pg.Surface((380, 140), pg.SRCALPHA)
        panel.fill((14, 18, 32, 220))
        self.screen.blit(panel, (WIDTH // 2 - 190, HEIGHT // 2 - 70))
        pg.draw.rect(self.screen, HUD_BORDER, (WIDTH // 2 - 190, HEIGHT // 2 - 70, 380, 140), 3)
        self.draw_text("PAUSED", 56, GOLD, WIDTH // 2, HEIGHT // 2)

    def draw_game_over_overlay(self) -> None:
        panel = pg.Surface((760, 300), pg.SRCALPHA)
        panel.fill((24, 10, 16, 230))
        self.screen.blit(panel, (WIDTH // 2 - 380, HEIGHT // 2 - 150))
        pg.draw.rect(self.screen, RED, (WIDTH // 2 - 380, HEIGHT // 2 - 150, 760, 300), 3)

        self.draw_text("INK RAN DRY", 72, RED, WIDTH // 2, HEIGHT // 2 - 65)
        self.draw_text(self.game_over_reason, 30, WHITE, WIDTH // 2, HEIGHT // 2 - 5)
        self.draw_text(f"Score: {self.score}", 34, WHITE, WIDTH // 2, HEIGHT // 2 + 45)
        self.draw_text("ENTER to retry this wave  |  R for new run", 28, GOLD, WIDTH // 2, HEIGHT // 2 + 95)

    def draw_world(self) -> None:
        self.enemies.draw(self.screen)
        self.pickups.draw(self.screen)
        self.projectiles.draw(self.screen)
        self.effects.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)

    def draw(self) -> None:
        self.backdrop.draw(self.screen)

        if self.state == "title":
            self.draw_title_screen()
        else:
            self.draw_world()
            self.draw_hud()

            if self.state == "wave_clear":
                self.draw_wave_clear_overlay()
            elif self.state == "game_over":
                self.draw_game_over_overlay()

            if self.pause and self.state == "playing":
                self.draw_pause_overlay()

        self.screen.blit(self.scanlines, (0, 0))
        pg.display.flip()

    async def run(self) -> None:
        while self.running:
            self.dt_seconds = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update()
            self.draw()
            # Required for browser/wasm targets so the event loop can yield.
            await asyncio.sleep(0)

        pg.quit()


async def main() -> None:
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
