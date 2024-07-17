from typing import Iterator, Tuple, List, TYPE_CHECKING
import random
import tcod

from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from entity import Entity

"""
RectangularRoom class

Methods : 
    __init__ : initialize a rectangular room starting at (x,y) cordinate and with width and height
    Input :
        > x - int number for x cordinate
        > y - int number for y cordinate
        > width - int number for the room width
        > height = int number for th room height

    center : method to finde the center of the room
        Return : cordinate (x,y) that represent the senter of the room

    inner : slice the first row and column of the room to prevent non-intresects larger rooms
        Return : the sliced room

    intrsects : chack if this room is overlap with other room
        Input : 
            > other - other room to chack if intersects
        Return : True if this room intersect with the other
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
tunnle_between: method to create a tunnle between two points
                useing Bresenham line to find a path between to points
    Input :
        > start : the starting point
        > end : the ending point
    Yield : a series of x,y values with and end resulf of 'L' shpe path between the points
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
generate_dungeon : generat a dungeon with rooms randomly scattered on the map
                   and path's between the rooms
    Input :
        > max_rooms - number of maximum  rooms to generate
        > room_min_size - minimum width / height of a room
        > room_max_size - maximum width / height of a room
        > map_width - the map width
        > map_height - the map height
        > player - to place at the first generated room center as a starting position
    Output : dungen map with the player in the first generted room
"""
def generate_dungeon(
        max_rooms:int,
        room_min_size:int,
        room_max_size:int,
        map_width:int,
        map_height:int,
        player:'Entity'
    ) -> GameMap:
    
    dungeon = GameMap(map_width, map_height)

    rooms: List[RectangularRoom] = []

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
            player.x, player.y = new_room.center

        else:
            for x,y in tunnle_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x,y] = tile_types.floor
        print(new_room.x1,new_room.x2,new_room.y1,new_room.y2, new_room.inner, sep='\t')
        rooms.append(new_room)

    return dungeon

