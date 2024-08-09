import tcod
import copy

import entity_factories
import color
from engine import Engine
from procgen import generate_dungeon

def main() -> None:
    # screan size is * 16 pixels in cmd chars
    screan_width = 100 #80
    screan_height = 60 #50

    # map size bottom 5 cmd chars will be use later
    map_width = 100
    map_height = 53
    
    # inisilize rooms parmeters
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monster_per_room = 3
    #load the img file we will use
    tileset = tcod.tileset.load_tilesheet(
        "image.png",32,8,tcod.tileset.CHARMAP_TCOD
    )

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)
    engine.game_map = generate_dungeon(
        max_rooms = max_rooms,
        room_min_size = room_min_size,
        room_max_size = room_max_size,
        map_width = map_width,
        map_height = map_height,
        max_monster_per_room = max_monster_per_room,
        engine=engine)
    
    engine.update_fov()

    engine.message_log.add_messge(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )

    #creating the screan
    with tcod.context.new_terminal(
        screan_width,
        screan_height,
        tileset=tileset,
        title='Yet Another Roguelike Game',
        vsync=True,
    ) as context:
        #creates our “console” which is what we’ll be drawing to
        root_console = tcod.Console(screan_width, screan_height, order='F')
        
        #game loop
        while True:
            #draw '@' in location x,y (x=0,y=0 is the top  left corner)
            engine.render(console=root_console, context=context)

            #updates the screen display.
            engine.event_handler.handle_events()
            

if __name__ == "__main__":
    main()