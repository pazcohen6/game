from typing import Optional
import tcod
from actions import Action, EscapeAction, MovementAction


# EventHandler class that processes game events and dispatches corresponding actions.
# Subclass of tcod's EevntDispatch
class EventHandler(tcod.event.EventDispatch[Action]):

    # Handle the quit event by raising SystemExit to exit the game.
    def ev_quit(self, event:tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    # Handle keydown events and map them to corresponding actions.
    # The method receive a key press event and return an Action subclass or None
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        
        action : Optional[Action] = None

        # get the pressed key form the system
        key = event.sym

        # actions to move up, down, left and right.
        if key == tcod.event.K_UP:
            action = MovementAction(dx = 0, dy = -1)
        elif key == tcod.event.K_DOWN:
            action = MovementAction(dx = 0, dy = 1)
        elif key == tcod.event.K_LEFT:
            action = MovementAction(dx = -1, dy = 0)
        elif key == tcod.event.K_RIGHT:
            action = MovementAction(dx = 1, dy = 0)

        # actions to move up(w), down(x), left(a), right(d)
        # or diagnal up-left(q), up-right(e), down-left(z), down-right(c)
        elif key == tcod.event.K_w:
            action = MovementAction(dx = 0, dy = -1)
        elif key == tcod.event.K_q:
            action = MovementAction(dx = -1, dy = -1)
        elif key == tcod.event.K_a:
            action = MovementAction(dx = -1, dy = 0)
        elif key == tcod.event.K_z:
            action = MovementAction(dx = -1, dy = 1)
        elif key == tcod.event.K_x:
            action = MovementAction(dx = 0, dy = 1)
        elif key == tcod.event.K_c:
            action = MovementAction(dx = 1, dy = 1)
        elif key == tcod.event.K_d:
            action = MovementAction(dx = 1, dy = 0)
        elif key == tcod.event.K_e:
            action = MovementAction(dx = 1, dy = -1)

        # action esc to Quit the game
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction()

        return action