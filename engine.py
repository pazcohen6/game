from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from input_handlers import EventHandler

if TYPE_CHECKING:
    from entity import Entity
    from game_map import GameMap

"""
Engine
Methods : TODO

"""
class Engine:
    game_map: GameMap

    def __init__(self, player: Entity):
        self.event_handler: EventHandler = EventHandler(self)
        self.player = player
        
    def handle_enemy_turn(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                entity.ai.perform()
    
    def update_fov(self) -> None :
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles['transparent'],
            (self.player.x, self.player.y),
            radius=8,
        )
        #set explored arrat to include things in the visible array with the or '|=' operation
        self.game_map.explored |= self.game_map.visible


    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        context.present(console)

        console.clear()