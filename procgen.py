from typing import Dict, Iterator, Tuple, List, TYPE_CHECKING
import random
import tcod
from itertools import product

import entity_factories
from game_map import GameMap
import tile_types

from entity import Entity

if TYPE_CHECKING:
    from engine import Engine
    



max_items_by_floor = [
    (1,1),
    (4,2),
]

max_monsters_by_floor = [
    (1,2),
    (4,3),
    (6,5),
]

item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.health_potion, 35)],
    2: [(entity_factories.confusion_scroll, 10)],
    4: [(entity_factories.lightning_scroll, 25), (entity_factories.sword, 5)],
    6: [(entity_factories.firecube_scroll, 25), (entity_factories.chain_mail, 15), (entity_factories.sword, 5)]
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.troll, 60)]
}

"""
    TODO
"""
def get_max_value_for_floor(
        max_value_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    current_value = 0

    for floor_minimimum, value in max_value_by_floor:
        if floor_minimimum > floor:
            break
        else:
            current_value = value

    return current_value

"""
    TODO
"""
def get_entities_at_random(
        weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
        number_of_entities: int,
        floor: int,
) -> List[Entity]:
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                weighted_chance = value[1]

                entity_weighted_chances[entity] = weighted_chance
    
    entities = list(entity_weighted_chances.keys())
    entity_weighted_chances_values = list(entity_weighted_chances.values())

    chosen_entities = random.choices(
        entities, weights = entity_weighted_chances_values, k = number_of_entities
    )

    return chosen_entities

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
    def __init__(self, x: int, y: int, width: int, height: int) :
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
        > floor_number (int): The player current floor number.

    Return:
        > None
"""
def place_entities(room:RectangularRoom, dungeon:GameMap, floor_number: int) -> None:
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )

    monsters : List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number
    )
    items : List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number
    )

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)
        
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)

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
        
        x_slice, y_slice = new_room.inner
        for x in range(x_slice.start, x_slice.stop):
            for y in range(y_slice.start, y_slice.stop):
                dungeon.tiles[x,y] = tile_types.new_random_floor()

        if len(rooms) == 0:
            player.place(*new_room.center, dungeon)

        else:
            for x,y in tunnle_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x,y] = tile_types.new_random_floor()
            
            center_of_last_room = new_room.center


        place_entities(new_room, dungeon, engine.game_world.current_floor)

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room

        rooms.append(new_room)

    return dungeon