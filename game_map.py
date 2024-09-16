from __future__ import annotations
from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

"""
GameMap class:
    Represents the game map, including the tiles and entities present on it.
    Handles map rendering, entity management, and tile visibility.

Attributes:
    engine (Engine):
        The engine instance controlling the game. Used for interacting with the game state.
    width (int):
        The width of the game map in tiles.
    height (int):
        The height of the game map in tiles.
    entities (set[Entity]):
        A set of entities present on the map.
    tiles (np.ndarray):
        A 2D array representing the map's tiles. Initialized to wall tiles by default.
    visible (np.ndarray):
        A 2D array indicating which tiles are currently visible.
    explored (np.ndarray):
        A 2D array indicating which tiles have been explored.
    downstairs_location (Tuple[int, int]):
        The (x, y) coordinates of the stairs leading to the next floor.

Methods:
    __init__:
        Initializes a new game map with the given dimensions and optionally with
        initial entities.

        Parameters:
            engine (Engine): The engine instance controlling the game.
            width (int): The width of the map.
            height (int): The height of the map.
            entities (Iterable[Entity]): Initial entities to place on the map.

    gamemap (property):
        Returns the GameMap instance.

    actors (property):
        Iterates over living actors on the map.
        
        Yields:
            Actor: Each living actor on the map.
    
    items (property):
        Iterates over items on the map.
        
        Yields:
            Item: Each item on the map.

    get_blocking_entity_at_location:
        Retrieves an entity at a specific location that blocks movement.

        Parameters:
            location_x (int): The x-coordinate of the location.
            location_y (int): The y-coordinate of the location.

        Returns:
            Optional[Entity]: The blocking entity, or None if no entity blocks the location.

    get_actor_at_location:
        Retrieves an actor at a specific location.

        Parameters:
            x (int): The x-coordinate of the location.
            y (int): The y-coordinate of the location.

        Returns:
            Optional[Actor]: The actor at the location, or None if no actor is present.

    in_bounds:
        Checks if a location is within the map's bounds.

        Parameters:
            x (int): The x-coordinate to check.
            y (int): The y-coordinate to check.

        Returns:
            bool: True if the location is within bounds, False otherwise.

    render:
        Renders the map to the console, displaying tiles and entities.

        Parameters:
            console (Console): The console instance to render to.
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

        self.downstairs_location = (0,0)

    @property
    def gamemap(self) -> GameMap:
        return self
    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_ntity_at_location(self, location_x : int, location_y : int) ->Optional[Entity]:
        
        for entity in self.entities:
            if (entity.blocks_movement and
                entity.x == location_x and
                entity.y == location_y):
                return entity
        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x:int, y:int) -> bool:
        return 0 <= x < self.width and 0 <= y <self.height
    
    def render(self, console: Console) -> None:
        console.tiles_rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key= lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=entity.color
                )

"""
GameWorld class:
    Manages the settings and state of the game world. Handles floor generation,
    including room size, monster and item limits, and current floor tracking.

Attributes:
    engine (Engine):
        The engine instance controlling the game. Used for interacting with the game state.
    map_width (int):
        The width of the game map.
    map_height (int):
        The height of the game map.
    max_rooms (int):
        The maximum number of rooms that can be generated on each floor.
    room_min_size (int):
        The minimum size for rooms generated on the map.
    room_max_size (int):
        The maximum size for rooms generated on the map.
    max_monsters_per_room (int):
        The maximum number of monsters that can spawn in each room.
    max_items_per_room (int):
        The maximum number of items that can spawn in each room.
    current_floor (int):
        Tracks the current floor number in the dungeon.

Methods:
    __init__:
        Initializes a new GameWorld instance with the specified settings.

        Parameters:
            engine (Engine): The engine instance controlling the game.
            map_width (int): The width of the game map.
            map_height (int): The height of the game map.
            max_rooms (int): The maximum number of rooms per floor.
            room_min_size (int): The minimum size for generated rooms.
            room_max_size (int): The maximum size for generated rooms.
            max_monsters_per_room (int): The maximum number of monsters per room.
            max_items_per_room (int): The maximum number of items per room.
            current_floor (int): The starting floor number (default is 0).

    generate_floor:
        Generates a new floor, including rooms, monsters, and items.
        Increases the current floor count by one and sets the newly generated
        map as the active game map.

        Returns:
            None
"""
class GameWorld:
    def __init__(
            self,
            *,
            engine: Engine,
            map_width: int,
            map_height: int,
            max_rooms: int,
            room_min_size: int,
            room_max_size: int,
            max_monsters_per_room: int,
            max_items_per_room: int,
            current_floor: int= 0,
        ):

        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.max_monsters_per_room = max_monsters_per_room
        self.max_items_per_room = max_items_per_room

        self.current_floor = current_floor
    
    def generate_floor(self) -> None:
        from procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms= self.max_rooms,
            room_min_size= self.room_min_size,
            room_max_size= self.room_max_size,
            map_width= self.map_width,
            map_height= self.map_height,
            max_monsters_per_room= self.max_monsters_per_room,
            max_items_per_room= self.max_items_per_room,
            engine= self.engine,
        )
        