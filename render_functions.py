from __future__ import annotations

from typing import TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine
    from game_map import GameMap

"""
get_names_at_location function:
    Retrieves the names of entities located at the specified coordinates on the game map.
    
    Parameters:
        x (int): The x-coordinate on the game map.
        y (int): The y-coordinate on the game map.
        game_map (GameMap): The game map to check for entities.
        
    Return:
        > str: A comma-separated list of names of entities at the given coordinates, capitalized.
"""
def get_names_at_location(x: int, y:int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""
    
    name = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return name.capitalize()

"""
render_bar function:
    Renders a health bar on the console, indicating the current and maximum values.

    Parameters:
        console (Console): The console to render the bar onto.
        current_value (int): The current value to display on the bar.
        maximum_value (int): The maximum value of the bar.
        total_width (int): The total width of the bar on the console.
    
    Return:
        > None
"""
def render_bar(
        console: Console, current_value: int, maximum_value: int, total_width: int
        ) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=0, y=52, width=total_width, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x=0, y=52, width=bar_width, height=1, ch=1, bg=color.bar_filled
        )

    console.print(
        x=1, y=52, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
    )

"""
render_names_at_mouse_location function:
    Renders the names of entities at the current mouse location on the console.

    Parameters:
        console (Console): The console to render the names onto.
        x (int): The x-coordinate on the console for rendering the names.
        y (int): The y-coordinate on the console for rendering the names.
        engine (Engine): The game engine, used to get the current mouse location and game map.

    Return:
        > None
"""
def render_names_at_mouse_location(
        console: Console, x: int, y: int, engine: Engine
) -> None :
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x= mouse_x, y= mouse_y, game_map= engine.game_map
    )

    console.print(x= x, y= y, string= names_at_mouse_location)