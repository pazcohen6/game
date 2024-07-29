from __future__ import annotations
from typing import Iterable, Optional, TYPE_CHECKING

import numpy as np
from tcod.console import Console

import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

"""
GameMap class that represent the game map
Method : TODO
"""
class GameMap:
    def __init__(self, engine: Engine, width:int, height:int, entities: Iterable[Entity] = ()):
        self.engine = engine
        self.width = width
        self.height = height

        self.entities = set(entities)
        
        self.tiles = np.full((width,height), fill_value=tile_types.wall, order='F')

        self.visible = np.full((width, height), fill_value=False, order="F")
        self.explored = np.full((width, height), fill_value = False, order='F')

    def get_blocking_ntity_at_location(self, location_x : int, location_y : int) ->Optional[Entity]:
        
        for entity in self.entities:
            if (entity.block_movement and
                entity.x == location_x and
                entity.y == location_y):
                return entity
        return None

    def in_bounds(self, x:int, y:int) -> bool:
        return 0 <= x < self.width and 0 <= y <self.height
    
    def render(self, console: Console) -> None:
        console.tiles_rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        for entity in self.entities:
            if self.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.char, fg=entity.color)