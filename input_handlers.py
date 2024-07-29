from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import tcod.event
from actions import Action, EscapeAction, BumpAction

if TYPE_CHECKING:
    from engine import Engine


# EventHandler class that processes game events and dispatches corresponding actions.
# Subclass of tcod's EevntDispatch
# TODO
class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine
    
    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue
            
            action.preform()

            self.engine.handle_enemy_turn()
            self.engine.update_fov()

    # Handle the quit event by raising SystemExit to exit the game.
    def ev_quit(self, event:tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    # Handle keydown events and map them to corresponding actions.
    # The method receive a key press event and return an Action subclass or None
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        
        action : Optional[Action] = None

        # get the pressed key form the system
        key = event.sym

        player = self.engine.player

        # actions to move up, down, left and right.
        if key == tcod.event.K_UP:
            action = BumpAction(player, dx = 0, dy = -1)
        elif key == tcod.event.K_DOWN:
            action = BumpAction(player, dx = 0, dy = 1)
        elif key == tcod.event.K_LEFT:
            action = BumpAction(player, dx = -1, dy = 0)
        elif key == tcod.event.K_RIGHT:
            action = BumpAction(player, dx = 1, dy = 0)

        # actions to move up(w), down(x), left(a), right(d)
        # or diagnal up-left(q), up-right(e), down-left(z), down-right(c)
        elif key == tcod.event.K_w:
            action = BumpAction(player, dx = 0, dy = -1)
        elif key == tcod.event.K_q:
            action = BumpAction(player, dx = -1, dy = -1)
        elif key == tcod.event.K_a:
            action = BumpAction(player, dx = -1, dy = 0)
        elif key == tcod.event.K_z:
            action = BumpAction(player, dx = -1, dy = 1)
        elif key == tcod.event.K_x:
            action = BumpAction(player, dx = 0, dy = 1)
        elif key == tcod.event.K_c:
            action = BumpAction(player, dx = 1, dy = 1)
        elif key == tcod.event.K_d:
            action = BumpAction(player, dx = 1, dy = 0)
        elif key == tcod.event.K_e:
            action = BumpAction(player, dx = 1, dy = -1)

        # action esc to Quit the game
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction(player)

        return action