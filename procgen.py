from typing import Iterator, Tuple, List, TYPE_CHECKING
import random
import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine

"""
RectangularRoom class:
    This class defines a rectangular room in a dungeon.

Methods:
    __init__:
        Initializes a rectangular room starting at (x, y) coordinates with
        the specified width and height.

        Input:
            > x (int): The x-coordinate of the room's starting position.
            > y (int): The y-coordinate of the room's starting position.
            > width (int): The width of the room.
            > height (int): The height of the room.

    center:
        Calculates and returns the center coordinates of the room.

        Return:
            > Tuple[int, int]: A tuple representing the (x, y) coordinates of the room's center.

    inner:
        Returns a slice of the room's inner area, excluding the outer walls.

        Return:
            > Tuple[slice, slice]: Slices representing the inner area of the room.

    intersects:
        Checks if this room intersects with another room.

        Input:
            > other (RectangularRoom): Another room to check for intersection.

        Return:
            > bool: True if this room intersects with the other room, False otherwise.
"""
class RectangularRoom:
    def __init__(self, x:int, y:int, width:int, height:int) :
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int,int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y
    
    @property
    def inner(self) -> Tuple[slice, slice]:
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)
    
    def intersects(self, other: 'RectangularRoom') -> bool:
        return (self.x1 <= other.x2 
                and self.x2 >= other.x1 
                and self.y1 <= other.y2 
                and self.y2 >= other.y1)

"""
tunnel_between function:
    Creates an 'L'-shaped tunnel between two points using Bresenham's line algorithm.

    Input:
        > start (Tuple[int, int]): The starting point of the tunnel.
        > end (Tuple[int, int]): The ending point of the tunnel.

    Yield:
        > Iterator[Tuple[int, int]]: A series of (x, y) coordinates representing the tunnel.
"""        
def tunnle_between(
        start: Tuple[int,int], end: Tuple[int,int]
) -> Iterator[Tuple[int,int]]:
    x1,y1 = start
    x2,y2 = end

    # randomly decide the corner point  
    if random.random() < 0.5:
        corner_x, corner_y = x2, y1
    else:
        corner_x, corner_y = x1, y2

    for x,y in tcod.los.bresenham((x1,y1), (corner_x,corner_y)).tolist():
        yield x,y

    for x,y in tcod.los.bresenham((corner_x,corner_y), (x2,y2)).tolist():
        yield x,y

"""
place_entities function:
    Places a random number of monsters in a given room within the dungeon.

    Input:
        > room (RectangularRoom): The room in which to place the monsters.
        > dungeon (GameMap): The game map where the room is located.
        > maximum_monster (int): The maximum number of monsters to place in the room.
        > maximum_item (int): The maximum number of items to place in the room.

    Return:
        > None
"""
def place_entities(
        room:RectangularRoom, dungeon:GameMap, maximum_monster:int, maximum_items: int,
) -> None:
    number_of_monsters = random.randint(0, maximum_monster)
    number_of_items = random.randint(0, maximum_items)

    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x ==x and entity.y==y for entity in dungeon.entities):
            if random.random() < 0.8:
                entity_factories.orc.spawn(dungeon, x, y)
            else:
                entity_factories.troll.spawn(dungeon, x, y)

    for i in range(number_of_items):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)
        
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            item_chance = random.random()
            
            if item_chance < 0.5:
                entity_factories.health_potion.spawn(dungeon, x, y)
            if item_chance < 0.65:
                entity_factories.firecube_scroll.spawn(dungeon, x, y)
            elif item_chance < 0.80:
                entity_factories.confusion_scroll.spawn(dungeon, x, y)
            else:
                entity_factories.lightning_scroll.spawn(dungeon, x, y)

"""
generate_dungeon function:
    Generates a dungeon map with randomly scattered rooms connected by tunnels.
    Places the player in the first generated room and populates the rooms with monsters.

    Input:
        > max_rooms (int): The maximum number of rooms to generate.
        > room_min_size (int): The minimum width/height of a room.
        > room_max_size (int): The maximum width/height of a room.
        > map_width (int): The width of the dungeon map.
        > map_height (int): The height of the dungeon map.
        > max_monsters_per_room (int): The maximum number of monsters per room.
        > max_items_per_room (int): The maximum number of items per room.
        > engine (Engine): The game engine, including the player entity.

    Return:
        > GameMap: The generated dungeon map with rooms, tunnels, and entities.
"""
def generate_dungeon(
        max_rooms:int,
        room_min_size:int,
        room_max_size:int,
        map_width:int,
        map_height:int,
        max_monsters_per_room: int,
        max_items_per_room: int,
        engine: 'Engine',
    ) -> GameMap:
    
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    center_of_last_room = (0, 0)

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x=x, y=y, width=room_width, height=room_height)

        if any(new_room.intersects(other_room) for other_room in rooms):
            continue
        
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            player.place(*new_room.center, dungeon)

        else:
            for x,y in tunnle_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x,y] = tile_types.floor
            
            center_of_last_room = new_room.center
        
        place_entities(new_room,dungeon,max_monsters_per_room, max_items_per_room)

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room

        rooms.append(new_room)

    return dungeon

