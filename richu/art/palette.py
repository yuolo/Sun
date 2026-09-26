"""The 32-colour palette and time-of-day remaps.

Colours 0–15 are Pyxel's default palette; 16–31 add the tones of a Chinese
mountain: vermilion walls, jade pines, ochre, rice paper, ink, lantern gold,
mist, night blue, dawn rose. Time of day is shown the way 8-bit games did it:
the same picture is drawn with a colour remap (``pyxel.pal``).
"""
from __future__ import annotations

PALETTE = [
    0x000000,  # 0  black
    0x2B335F,  # 1  navy
    0x7E2072,  # 2  purple
    0x19959C,  # 3  teal
    0x8B4852,  # 4  brown (plum)
    0x395C98,  # 5  dark blue
    0xA9C1FF,  # 6  light blue
    0xEEEEEE,  # 7  white
    0xD4186C,  # 8  red
    0xD38441,  # 9  orange
    0xE9C35B,  # 10 yellow
    0x70C6A9,  # 11 mint
    0x7696DE,  # 12 periwinkle
    0xA3A3A3,  # 13 grey
    0xFF9798,  # 14 pink
    0xEDC7B0,  # 15 peach
    0xC23B22,  # 16 vermilion 朱
    0x7A1E17,  # 17 lacquer (dark vermilion)
    0x2E6B4F,  # 18 pine (dark jade)
    0x4E9A6A,  # 19 jade 翠
    0xB08A4A,  # 20 ochre / bronze
    0xF2E6C9,  # 21 rice paper
    0x1C1A24,  # 22 ink 墨
    0xF5B83D,  # 23 gold (lantern)
    0xC9D3DC,  # 24 mist
    0x101830,  # 25 night
    0x5B4A7A,  # 26 dusk violet
    0xF08A6B,  # 27 dawn rose
    0x6F6A64,  # 28 stone
    0x5E7A3C,  # 29 moss
    0x3A2E28,  # 30 dark wood
    0xFFE9A8,  # 31 lamplight
]

BLACK, NAVY, PURPLE, TEAL, PLUM, DARK_BLUE, LIGHT_BLUE, WHITE = range(8)
RED, ORANGE, YELLOW, MINT, PERIWINKLE, GREY, PINK, PEACH = range(8, 16)
VERMILION, LACQUER, PINE, JADE, OCHRE, PAPER, INK, GOLD = range(16, 24)
MIST, NIGHT, DUSK, ROSE, STONE, MOSS, WOOD, LAMP = range(24, 32)

# Tone colours for pinyin (1–4, neutral), readable on paper.
TONE_COLORS = {1: VERMILION, 2: 19, 3: DARK_BLUE, 4: PURPLE, 0: STONE}


def _remap(pairs: dict[int, int]) -> list[int]:
    table = list(range(len(PALETTE)))
    for a, b in pairs.items():
        table[a] = b
    return table


# Remaps for scene art. Keys: colour as painted (daylight) → colour shown.
TIMES: dict[str, list[int]] = {
    'day': _remap({}),
    'golden': _remap({
        LIGHT_BLUE: PEACH, MIST: PEACH, WHITE: LAMP, PERIWINKLE: 14, DARK_BLUE: DUSK,
        JADE: MOSS, MINT: YELLOW, GREY: 15, TEAL: MOSS,
    }),
    'sunset': _remap({
        LIGHT_BLUE: ROSE, MIST: 14, WHITE: PEACH, PERIWINKLE: DUSK, DARK_BLUE: PURPLE, NAVY: PURPLE,
        JADE: PINE, MINT: OCHRE, PAPER: 15, GREY: 14, TEAL: PINE, STONE: PLUM, YELLOW: ORANGE, PEACH: ROSE,
    }),
    'dusk': _remap({
        LIGHT_BLUE: DUSK, MIST: DUSK, WHITE: MIST, PERIWINKLE: DUSK, DARK_BLUE: NAVY, TEAL: NAVY,
        JADE: PINE, PINE: NAVY, MINT: PINE, PAPER: MIST, GREY: STONE, STONE: DUSK, PEACH: GREY,
        OCHRE: PLUM, YELLOW: OCHRE, VERMILION: PLUM, 15: GREY, MOSS: PINE, WOOD: NIGHT,
    }),
    'night': _remap({
        LIGHT_BLUE: NAVY, MIST: DARK_BLUE, WHITE: 12, PERIWINKLE: NAVY, DARK_BLUE: NIGHT, TEAL: NIGHT,
        JADE: NAVY, PINE: NIGHT, MINT: NAVY, PAPER: GREY, GREY: DARK_BLUE, STONE: NAVY, PEACH: STONE,
        OCHRE: NAVY, YELLOW: GOLD, VERMILION: LACQUER, 15: STONE, MOSS: NIGHT, WOOD: NIGHT, PLUM: NIGHT,
        ORANGE: PLUM, ROSE: PLUM, LACQUER: NIGHT, DUSK: NAVY, PINK: PLUM,
        INK: NIGHT, BLACK: NIGHT, NAVY: NIGHT, PURPLE: NIGHT,
    }),
    'predawn': _remap({
        LIGHT_BLUE: DUSK, MIST: PERIWINKLE, WHITE: MIST, PERIWINKLE: DUSK, DARK_BLUE: NAVY, TEAL: NAVY,
        JADE: NAVY, PINE: NIGHT, MINT: DARK_BLUE, PAPER: MIST, GREY: STONE, STONE: DUSK, PEACH: 14,
        OCHRE: PLUM, YELLOW: ROSE, VERMILION: LACQUER, 15: GREY, MOSS: NAVY, WOOD: NIGHT, PLUM: NAVY,
    }),
    'dawn': _remap({
        LIGHT_BLUE: PEACH, MIST: 15, WHITE: LAMP, PERIWINKLE: ROSE, DARK_BLUE: DUSK, TEAL: PINE,
        JADE: PINE, MINT: MOSS, GREY: 15, STONE: PLUM, PAPER: LAMP,
    }),
}

# People and props change more gently than the landscape.
FIGURE_TIMES: dict[str, list[int]] = {
    'day': _remap({}),
    'golden': _remap({WHITE: LAMP}),
    'sunset': _remap({WHITE: PEACH, LIGHT_BLUE: 14}),
    'dusk': _remap({WHITE: MIST, PEACH: 14, PAPER: MIST, YELLOW: OCHRE}),
    'night': _remap({
        WHITE: MIST, PAPER: GREY, PEACH: STONE, 15: STONE, YELLOW: OCHRE, VERMILION: PLUM, JADE: PINE, MOSS: PINE,
        OCHRE: PLUM, LIGHT_BLUE: PERIWINKLE, GREY: STONE, MINT: TEAL, ORANGE: PLUM, 14: PLUM,
    }),
    'predawn': _remap({WHITE: MIST, PAPER: MIST, PEACH: 14, YELLOW: OCHRE, 15: 14}),
    'dawn': _remap({WHITE: LAMP}),
}

# Night colours lit by a lantern: dark tones warm up near the light.
LAMPLIT = _remap({
    NIGHT: WOOD, NAVY: PLUM, DARK_BLUE: OCHRE, STONE: OCHRE, 12: PEACH, GREY: PEACH,
    LACQUER: VERMILION, DUSK: PLUM, PLUM: VERMILION,
})


def apply() -> None:
    import pyxel

    pyxel.colors[:] = PALETTE


def set_time(time: str) -> None:
    """Remaps the palette for scene art; call reset() before drawing the UI."""
    import pyxel

    for i, c in enumerate(TIMES.get(time, TIMES['day'])):
        if c != i:
            pyxel.pal(i, c)


def set_figure_time(time: str, lit: bool = False) -> None:
    """Palette remap for people and props; a lantern keeps them in their own colours."""
    import pyxel

    if lit and time in ('night', 'dusk', 'predawn'):
        return
    for i, c in enumerate(FIGURE_TIMES.get(time, FIGURE_TIMES['day'])):
        if c != i:
            pyxel.pal(i, c)


def reset() -> None:
    import pyxel

    pyxel.pal()
