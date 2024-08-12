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
        ("light", graphic_dt), # Graphics for when the tile is in FOV
    ]
)

"""
new_tile function:
    Creates a new tile with the specified properties.

    Parameters:
        walkable (int): Whether the tile is walkable.
        transparent (int): Whether the tile is transparent.
        dark (Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]):
            Graphics for when the tile is not in FOV.
        light (Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]):
            Graphics for when the tile is in FOV.

    Return:
        > np.ndarray: A numpy array representing the tile with the specified properties.
"""
def new_tile(
    *, # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light:Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    return np.array((walkable,transparent,dark,light), dtype=tile_dt)

# Represent unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255,255,255), (0,0,0)), dtype=graphic_dt)

#  Represents a floor tile in the game. It is walkable and transparent,
floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "),(255,255,255), (50,50,150)),
    light=(ord(" "),(255,255,255), (200,180,50))
)

# Represents a wall tile in the game. It is not walkable and not transparent,
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (100,100,100), (0,0,100)),
    light=(ord("#"), (255,255,255), (130,110,50))
)