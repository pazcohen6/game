import tcod

from input_handlers import EventHandler
from entity import Entity
from engine import Engine
from procgen import generate_dungeon

def main() -> None:
    # screan size is * 16 pixels in cmd chars
    screan_width = 100 #80
    screan_height = 60 #50

    # map size bottom 5 cmd chars will be use later
    map_width = 100
    map_height = 55
    
    # inisilize rooms parmeters
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    #load the img file we will use
    tileset = tcod.tileset.load_tilesheet(
        "image.png",32,8,tcod.tileset.CHARMAP_TCOD
    )

    event_handler = EventHandler()

    player = Entity(int(screan_width / 2), int(screan_height / 2), '@', (255,255,255))
    npc = Entity(int(screan_width / 2 - 5), int(screan_height / 2), '@', (255,255,0))
    entities = {player, npc}

    game_map = generate_dungeon(
        max_rooms,
        room_min_size,
        room_max_size,
        map_width,
        map_height,
        player)
    
    engine = Engine(entities=entities, event_handler=event_handler, game_map=game_map ,player=player)
    #creating the screan
    with tcod.context.new_terminal(
        screan_width,
        screan_height,
        tileset=tileset,
        title='Yet Another Roguelike Tutorial',
        vsync=True,
    ) as context:
        #creates our “console” which is what we’ll be drawing to
        root_console = tcod.Console(screan_width, screan_height, order='F')
        
        #game loop
        while True:
            #draw '@' in location x,y (x=0,y=0 is the top  left corner)
            engine.render(console=root_console, context=context)

            #updates the screen display.
            events = tcod.event.wait()

            engine.handle_events(events)
            

if __name__ == "__main__":
    main()