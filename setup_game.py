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
import input_handlers
from procgen import generate_dungeon

# Load the background imge and remove the alph channel.
# the image need to be 200 x 120 pixels
backround_image = tcod.image.load("spongebob.png")[:,:,:3]

"""
    TODO: Return a brand new game session as an Engine instance.
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
    engine.game_map = generate_dungeon(
        max_rooms = max_rooms,
        room_min_size = room_min_size,
        room_max_size = room_max_size,
        map_width = map_width,
        map_height = map_height,
        max_monsters_per_room = max_monsters_per_room,
        max_items_per_room = max_items_per_room,
        engine=engine,
    )
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )
    return engine
"""
    TODO: Load an Engine instance from a file.
"""
def load_game(filename: str) -> Engine:
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine
"""
    TODO: Handle the main menu rendering and input.
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