from typing import Tuple

import numpy as np

graphic_dt = np.dtype(
    [
        ("ch",np.int32), #unicode codepoint
        ("fg","3B"), #3 unsighned pytes for RGB colors
        ("bg","3B"),
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
    walkable=True, transparent=True, dark=(ord(" "),(255,255,255), (78,150,50)),
)
wall = new_tile(
    walkable=False, transparent=False, dark=(ord("#"), (102,51,0), (130,82,1)),
)