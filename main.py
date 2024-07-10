import tcod
from actions import EscapeAction, MovementAction
from input_handlers import EventHandler

def main() -> None:
    #screan size is * 16 pixels in cmd chars
    screan_witdth = 80
    screan_hight = 50
    
    #inisialist the player location on the screan
    player_x = int(screan_witdth / 2)
    player_y = int(screan_hight / 2)

    #load the img file we will use
    tileset = tcod.tileset.load_tilesheet(
        "image.png",32,8,tcod.tileset.CHARMAP_TCOD
    )

    event_handler = EventHandler()

    #creating the screan
    with tcod.context.new_terminal(
        screan_witdth,
        screan_hight,
        tileset=tileset,
        title='Yet Another Roguelike Tutorial',
        vsync=True,
    ) as context:
        #creates our “console” which is what we’ll be drawing to
        root_console = tcod.Console(screan_witdth, screan_hight, order='F')
        
        #game loop
        while True:
            #draw '@' in location x,y (x=0,y=0 is the top  left corner)
            root_console.print(x=player_x,y=player_y, string='@')

            #updates the screen display.
            context.present(root_console)
            root_console.clear()
            #gives us a way to exit
            for event in tcod.event.wait():
                action = event_handler.dispatch(event)

                if action is None:
                    continue
                
                if isinstance(action, MovementAction):
                    player_x += action.dx
                    player_y += action.dy
                
                elif isinstance(action,EscapeAction):
                    raise SystemExit()


if __name__ == "__main__":
    main()