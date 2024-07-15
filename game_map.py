import numpy as np
from tcod.console import Console

import tile_types

#class that represent the game map
class GameMap:
    def __init__(self, width:int, hight:int):
        self.width = width
        self.hight = hight
        self.tiles = np.full((width,hight), fill_value=tile_types.floor, order='F')

        self.tiles[30:33,22] = tile_types.wall

    def in_bounds(self, x:int, y:int) -> bool:
        return 0 <= x < self.width and 0 <= y <self.hight
    
    def render(self, console: Console) -> None:
        console.tiles_rgb[0:self.width, 0:self.hight] = self.tiles['dark']