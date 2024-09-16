"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional

import tcod

import color
from engine import Engine
import entity_factories
from game_map import GameWorld
import input_handlers

# Load the background imge and remove the alph channel.
# the image need to be 200 x 120 pixels
backround_image = tcod.image.load("spongebob.png")[:,:,:3]

"""
new_game function:
    Initializes and returns a new game session as an Engine instance. This function 
    creates a new player, sets up the game world, and generates the first floor.

Attributes:
    map_width (int):
        The width of the game map.
    map_height (int):
        The height of the game map.
    room_max_size (int):
        The maximum size of a room in the dungeon.
    room_min_size (int):
        The minimum size of a room in the dungeon.
    max_rooms (int):
        The maximum number of rooms to generate on the map.
    max_monsters_per_room (int):
        The maximum number of monsters that can spawn in a room.
    max_items_per_room (int):
        The maximum number of items that can spawn in a room.
    player (Actor):
        A copy of the player entity to be placed in the game world.
    engine (Engine):
        The core game engine that manages the game session.
    game_world (GameWorld):
        The object representing the game world and handling floor generation.

Return:
    > Engine: A new game engine instance initialized with the game world and player.
"""
def new_game() -> Engine:
    map_width = 100
    map_height = 53

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    max_monsters_per_room = 3
    max_items_per_room = 2

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)
    engine.game_world = GameWorld(
        engine = engine,
        max_rooms = max_rooms,
        room_min_size = room_min_size,
        room_max_size = room_max_size,
        map_width = map_width,
        map_height = map_height,
        max_monsters_per_room = max_monsters_per_room,
        max_items_per_room = max_items_per_room,
    )
    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )
    return engine

"""
load_game function:
    Loads an Engine instance from a saved file. This function decompresses and 
    deserializes the saved game data to restore a previously saved game session.

Attributes:
    filename (str):
        The path to the file containing the saved game data.

Return:
    > Engine: The game engine instance restored from the saved file.
"""
def load_game(filename: str) -> Engine:
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine

"""
MainMenu class:
    This class represents the main menu of the game, responsible for rendering the 
    menu options and handling user input, such as starting a new game, continuing 
    from a save file, or quitting the game.

Attributes:
    None

Methods:
    on_render:
        Renders the main menu on the screen, displaying the background and the
        available options for the player.

        Input:
            > console (tcod.console.Console): The console on which to render the menu.

        Return:
            > None

    ev_keydown:
        Handles keyboard input from the player in the main menu, allowing them to
        start a new game, continue from a saved game, or quit.

        Input:
            > event (tcod.event.KeyDown): The key press event captured from the player.

        Return:
            > Optional[input_handlers.BaseEventHandler]: The appropriate event handler based
              on the player's input (either loading a game, starting a new game, or exiting).
"""
class MainMenu(input_handlers.BaseEventHandler):
    def on_render(self, console: tcod.console.Console) -> None:
        console.draw_semigraphics(backround_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "TOMBS OF THE ANCIENT WARM",
            fg= color.menu_title,
            bg= color.black,
            alignment= tcod.CENTER,
            bg_blend= tcod.BKGND_ALPHA(64),
        )
        menu_width = 24
        for i, text in enumerate(
            ["[N] Play  new game", "[C] Continue last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg= color.menu_text,
                bg= color.black,
                alignment= tcod.CENTER,
                bg_blend= tcod.BKGND_ALPHA(64),
            )
        
    def ev_keydown(
            self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.K_c:
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No save game to load.")
            except Exception as exc:
                traceback.print_exc() # Print to stderr.
                return input_handlers.PopupMessage(self, f'Failed to load sve:\n{exc}')
        elif event.sym == tcod.event.K_n:
            return input_handlers.MainGameEventHandler(new_game())
        
        return None