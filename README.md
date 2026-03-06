# INKY 1.0 (Retro Remix)

A modernized pass on your original Pygame learning project.

The game keeps the same spirit: shoot RGB ink at moving blocks to discover and complete their hidden color combinations. The codebase is now state-driven, data-driven for waves, and easier to extend.

## Original vs Remix
<table>
  <tr>
    <th>Original (INKY 1.0)</th>
    <th>Retro Remix</th>
  </tr>
  <tr>
    <td><img src="inky.gif" alt="Original INKY gameplay" width="460" /></td>
    <td><img src="inky_remix.gif" alt="Retro Remix gameplay" width="460" /></td>
  </tr>
</table>

## Highlights
- Retro arcade presentation: scrolling grid, scanlines, chunky HUD, and wave overlays
- Cleaner architecture: explicit game states (`title`, `playing`, `wave_clear`, `game_over`)
- Data-driven enemy wave progression (instead of long conditional chains)
- Preserved RGB weapon identity (`Z` red burst, `X` bouncing green, `C` spinning blue)
- Wave progression upgrades:
  - Multi-shot unlocks (for the same ink cost) at higher waves
  - Player shot damage scales with wave
  - Enemy counts scale with wave
- Sustained pacing upgrades:
  - Faster passive ink regeneration
  - Higher potion drop rate
- Blue projectile visuals now use a circular energy shot
- Enemy spawn safety between waves (prevents spawning on top of player)
- HUD panel fades when enemies move behind it for better readability
- Basic persistent leaderboard (`leaderboard.txt`)

## Requirements
- Python 3.11+
- `pygame` 2.5+

## Run
```bash
python -m pip install -r requirements.txt
python main.py
```

## Play Online (GitHub Pages)
This repo now includes a Pages deploy workflow at `.github/workflows/deploy-pages.yml` that builds a browser bundle with `pygbag` and publishes `build/web`.

Expected URL after Pages is enabled:
- `https://leongbryan.github.io/inky1.0/`

One-time setup in GitHub:
1. Open your repository settings.
2. Go to `Pages`.
3. Set `Source` to `GitHub Actions`.
4. Push/merge this branch to `main` (or trigger the workflow manually in `Actions`).

Optional local web build:
```bash
python -m pip install -r requirements-web.txt
python -m pygbag --build --ume_block 0 .
```

## Controls
- Move: `WASD` or Arrow Keys
- Shoot: `Z` / `X` / `C`
- Pause: `P`
- Restart run: `R`
- Confirm / Continue: `Enter`
- Quit: `Esc`

## Notes
- Legacy files like `main_initial.py` are kept for historical reference.
- If an image asset is missing, the game now falls back to generated placeholders instead of crashing.
