from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from tcod.console import Console
import tcod.event
from actions import Action, BumpAction, EscapeAction, WaitAction

if TYPE_CHECKING:
    from engine import Engine

# Dictionary mapping keys to movement directions
MOVE_KEYS = {
    # Numpad keys :
    tcod.event.K_KP_1 : (-1,1),
    tcod.event.K_KP_2 : (0,1),
    tcod.event.K_KP_3 : (1,1),
    tcod.event.K_KP_4 : (-1,0),
    tcod.event.K_KP_6 : (1,0),
    tcod.event.K_KP_7 : (-1,-1),
    tcod.event.K_KP_8 : (0,-1),
    tcod.event.K_KP_9 : (1,-1),
    # wasd
    tcod.event.K_z : (-1,1),
    tcod.event.K_x : (0,1),
    tcod.event.K_c : (1,1),
    tcod.event.K_a : (-1,0),
    tcod.event.K_d : (1,0),
    tcod.event.K_q : (-1,-1),
    tcod.event.K_w : (0,-1),
    tcod.event.K_e : (1,-1),
}

# Set of keys used for waiting or pausing actions
WAIT_KEYS = {
    tcod.event.K_s,
    tcod.event.K_KP_5,
}

# Dictionary mapping cursor keys to movement values
CURSOR_Y_KEY = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: 10,
    tcod.event.K_PAGEDOWN: -10,

}

"""
EventHandler class:
    Processes game events and dispatches corresponding actions.
    Subclass of tcod's EventDispatch
Attributes:
    engine (Engine):
        The engine instance that handles the game state and logic.
Methods:
  handle_events:
        Processes events and dispatches them to the appropriate handlers.
        Parameters:
            context (tcod.context.Context): The context used to convert and handle events.
        Return:
            > None
    ev_mousemotion:
        Updates the mouse location in the engine based on mouse movement events.
        Parameters:
            event (tcod.event.MouseMotion): The mouse motion event.
        Return:
            > None
    ev_quit:
        Handles the quit event by raising SystemExit to exit the game.
        Parameters:
            event (tcod.event.Quit): The quit event.
        Return:
            > Optional[Action]
    on_render:
        Renders the current game state to the provided console.
        Parameters:
            console (tcod.console.Console): The console to which the game state is rendered.
        Return:
            > None
"""
class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine
    
    def handle_events(self, contxt: tcod.context.Context) -> None:
        for event in tcod.event.wait():
            contxt.convert_event(event)
            self.dispatch(event)

    def ev_mousemotion(self, event: tcod.context.Context) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y
    # Handle the quit event by raising SystemExit to exit the game.
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def on_render(self, console: tcod.console.Console) -> None:
        self.engine.render(console)

"""
MainGameEventHandler class:
    Handles events during the main game loop and processes actions.
    Inherits from EventHandler.

Methods:
    handle_events:
        Processes events and dispatches actions, then handles enemy turns and updates the FOV.

        Parameters:
            context (tcod.context.Context): The context used to convert and handle events.

        Return:
            > None

    ev_keydown:
        Handles keydown events and maps them to corresponding actions.

        Parameters:
            event (tcod.event.KeyDown): The keydown event.

        Return:
            > Optional[Action]
"""
class MainGameEventHandler(EventHandler):
    def handle_events(self, context: tcod.context.Context) -> None:
        for event in tcod.event.wait():
            context.convert_event(event)
            
            action = self.dispatch(event)

            if action is None:
                continue
        
            action.perform()

            self.engine.handle_enemy_turns()
            self.engine.update_fov() # Update the FOV before the players next action.

    # Handle keydown events and map them to corresponding actions.
    # The method receive a key press event and return an Action subclass or None
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        
        action : Optional[Action] = None

        # get the pressed key form the system
        key = event.sym

        player = self.engine.player

        # actions to move up, down, left and right.
        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        
        # action to wait and do mothing
        elif key in WAIT_KEYS:
            action = WaitAction(player)

        # action esc to Quit the game
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)
        
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)

        return action

"""
GameOverEventHandler class:
    Handles events when the game is over.
    Inherits from EventHandler.

Methods:
    handle_events:
        Processes events and dispatches actions.

        Parameters:
            context (tcod.context.Context): The context used to convert and handle events.

        Return:
            > None

    ev_keydown:
        Handles keydown events to determine if an escape action should be performed.

        Parameters:
            event (tcod.event.KeyDown): The keydown event.

        Return:
            > Optional[Action]
"""    
class GameOverEventHandler(EventHandler):
    def handle_events(self, context: tcod.context.Context) -> None:
        for event in tcod.event.wait():
            context.convert_event(event)
            
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym
        
        if key == tcod.event.K_ESCAPE:
            action = EscapeAction(self.engine.player)

        # no valid key was pressed
        return action

"""
HistoryViewer class:
    Displays the message history in a larger window that can be navigated.
    Inherits from EventHandler.

Attributes:
    log_length (int):
        The length of the message log.
    cursor (int):
        The current position of the cursor in the message log.

Methods:
    on_render:
        Renders the message history in a custom console.

        Parameters:
            console (Console): The console to which the message history is rendered.

        Return:
            > None

    ev_keydown:
        Handles keydown events to navigate the message history.

        Parameters:
            event (tcod.event.KeyDown): The keydown event.

        Return:
            > None
"""    
class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_leangth = len(engine.message_log.messages)
        self.cursor = self.log_leangth - 1

    def on_render(self, console: Console) -> None:
        super().on_render(console) # Draw the main state as the background.

        log_console = tcod.console.Console(console.width - 6, console.height - 6)
        
        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤ Message History ├", alignment=tcod.CENTER
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2 ,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEY:
            adjust = CURSOR_Y_KEY[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_leangth - 1
            elif adjust > 0 and self.cursor == self.log_leangth -1 :
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_leangth - 1))
        
        elif event.sym == tcod.event.K_HOME :
            self.cursor = 0 # Move directly to the top message.
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_leangth - 1 # Move directly to the last message.
        else :  # Any other key moves back to the main game state.
            self.engine.event_handler = MainGameEventHandler(self.engine)
