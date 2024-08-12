from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from input_handlers import MainGameEventHandler
from message_log import MessageLog
from render_functions import render_bar, render_names_at_mouse_location

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap
    from input_handlers import EventHandler

"""
Engine class:
    The central class that manages the game state, including the game map,
    player, and rendering. It handles game updates, field of view (FOV) calculations,
    and rendering of game elements.

Attributes:
    game_map (GameMap):
        The current game map instance that contains the game world and its entities.
    event_handler (EventHandler):
        The event handler responsible for processing game events, such as player input.
    message_log (MessageLog):
        The log that stores and displays messages (e.g., combat messages) during the game.
    mouse_location (Tuple[int, int]):
        The current mouse location on the screen.
    player (Actor):
        The player character entity in the game.

Methods:
    handle_enemy_turns:
        Processes actions for all enemy entities that are not the player. Calls
        the `perform` method of each enemy's AI to handle their turn.

        Return:
            > None

    update_fov:
        Updates the field of view (FOV) for the game map based on the player's current
        position. The visible tiles are updated, and the explored map is extended to
        include the newly visible tiles.

        Return:
            > None

    render:
        Renders the current game state to the provided console. This includes
        rendering the game map, message log, player health bar, and names of entities
        at the mouse location.

        Parameters:
            console (Console): The console to which the game state is rendered.

        Return:
            > None
"""
class Engine:
    game_map: GameMap

    def __init__(self, player: Actor):
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player
        
    def handle_enemy_turns(self) -> None:
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


    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x= 21, y= 53, width= 50 ,height= 5)
        render_bar(
            console= console,
            current_value= self.player.fighter.hp,
            maximum_value= self.player.fighter.max_hp,
            total_width= 20,
        )

        render_names_at_mouse_location(console= console, x = 21, y= 52, engine= self)