import tcod

from input_handlers import EventHandler
from entity import Entity
from engine import Engine
from game_map import GameMap

def main() -> None:
    #screan size is * 16 pixels in cmd chars
    screan_width = 140
    screan_hight = 100

    map_width = 140
    map_hight = 95

    #load the img file we will use
    tileset = tcod.tileset.load_tilesheet(
        "image.png",32,8,tcod.tileset.CHARMAP_TCOD
    )

    event_handler = EventHandler()

    player = Entity(int(screan_width / 2), int(screan_hight / 2), '@', (255,255,255))
    npc = Entity(int(screan_width / 2 - 5), int(screan_hight / 2), '@', (255,255,0))
    entities = {player, npc}

    game_map = GameMap(map_width, map_hight)
    
    engine = Engine(entities=entities, event_handler=event_handler, game_map=game_map ,player=player)
    #creating the screan
    with tcod.context.new_terminal(
        screan_width,
        screan_hight,
        tileset=tileset,
        title='Yet Another Roguelike Tutorial',
        vsync=True,
    ) as context:
        #creates our “console” which is what we’ll be drawing to
        root_console = tcod.Console(screan_width, screan_hight, order='F')
        
        #game loop
        while True:
            #draw '@' in location x,y (x=0,y=0 is the top  left corner)
            engine.render(console=root_console, context=context)

            #updates the screen display.
            events = tcod.event.wait()

            engine.handle_events(events)
            

if __name__ == "__main__":
    main()