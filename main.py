import tcod
import traceback

import color
import exceptions
import input_handlers
import setup_game

"""
save_game function:
    Saves the current game state if the event handler is an instance of the EventHandler class 
    and has an active Engine. The game state is serialized and written to a file.

Attributes:
    handler (input_handlers.BaseEventHandler):
        The event handler that manages the current game session.
    filename (str):
        The path to the file where the game state will be saved.

Return:
    > None
"""
def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game Saved.")

"""
main function:
    The entry point of the game, which sets up the screen, loads assets, and manages
    the main game loop. This function initializes the game window, handles game events, 
    and saves the game upon exit or exceptions.

Attributes:
    screan_width (int):
        The width of the game screen in characters (each character is 16x16 pixels).
    screan_height (int):
        The height of the game screen in characters.
    tileset (tcod.tileset.Tileset):
        The font or tileset used to display the game, loaded from an image file.
    handler (input_handlers.BaseEventHandler):
        The current event handler managing the game state and user inputs.
    context (tcod.context.Context):
        The terminal context responsible for presenting the game screen and handling
        the display buffer.
    root_console (tcod.console.Console):
        The console where all game graphics and text will be drawn.

Return:
    > None
"""
def main() -> None:
    # screan size is * 16 pixels in cmd chars
    screan_width = 100 #80
    screan_height = 60 #50

    #load the img file we will use
    tileset = tcod.tileset.load_tilesheet(
        "image.png",32,8,tcod.tileset.CHARMAP_TCOD
    )

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    #creating the screan
    with tcod.context.new_terminal(
        screan_width,
        screan_height,
        tileset=tileset,
        title='Yet Another Roguelike Game',
        vsync=True,
    ) as context:
        #creates our “console” which is what we’ll be drawing to
        root_console = tcod.console.Console(screan_width, screan_height, order='F')
        
        #game loop
        try:
            while True:
                root_console.clear()
                handler.on_render(console= root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception: # Handle exceptions in game.
                    traceback.print_exc() # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaveing:
            raise
        except SystemExit: # Save and quit.
            save_game(handler, "savegame.sav")
            raise
        except BaseException: # Save on any other unexpected exception.
            save_game(handler, "savegame.sav")
            raise

if __name__ == "__main__":
    main()