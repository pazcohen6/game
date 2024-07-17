from typing import Tuple

import numpy as np

graphic_dt = np.dtype(
    [
        ("ch",np.int32), # Unicode codepoint
        ("fg","3B"), # The foreground color as an RGB tuple (3 unsigned bytes).
        ("bg","3B"), # The background color as an RGB tuple (3 unsigned bytes).
    ]
)

tile_dt = np.dtype(
    [
        ("walkable", np.bool), # Ture if the tile is walkable
        ("transparent", np.bool), # true if the tile is doesn't block FOV
        ("dark", graphic_dt), # Graphics for when the tile is not in FOV
    ]
)

def new_tile(
    *, # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    #function to defining individual tile type
    return np.array((walkable,transparent,dark), dtype=tile_dt)

floor = new_tile(
    walkable=True, transparent=True, dark=(ord(" "),(255,255,255), (41,91,255)),
)
wall = new_tile(
    walkable=False, transparent=False, dark=(ord("#"), (0,0,200), (0,0,200)),
)